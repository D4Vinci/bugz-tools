import argparse, requests, concurrent.futures, json, sys, time, random, string
from terminaltables import AsciiTable as table
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

headers = {
	"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
	"accept-encoding": "gzip, deflate"
}

def create_table(rows, headers=["Path", "Status code", "Content length"]):
	all_rows = [headers]
	rows = sorted(rows)
	for row in rows:
		#Coloring rows
		row[0] = color.white + row[0] + color.reset
		if row[1]>=200:
			row[1] = color.green + str(row[1]) + color.reset
		elif row[1]>=300:
			row[1] = color.blue + str(row[1]) + color.reset
		elif row[1]>=400:
			row[1] = color.red + str(row[1]) + color.reset
		elif row[1]>=500:
			row[1] = color.magneta + str(row[1]) + color.reset
		else:
			row[1] = color.white + str(row[1]) + color.reset
		row[2] = color.white+color.Bold+str(row[2])+color.reset
		all_rows.append(row)
	t = table(all_rows,"")
	t.inner_column_border, t.outer_border, t.inner_heading_row_border, t.inner_footing_row_border = True, False, True, False
	t.justify_columns[0], t.justify_columns[1], t.justify_columns[2] = ['left', 'center', 'center']
	return ("\n"+t.table)

class color:
	reset     = '\033[0m'
	green     = reset + '\033[32m'
	blue      = reset + '\033[94m'
	red       = reset + '\033[31m'
	white     = reset + '\x1b[37m'
	magneta   = reset + '\x1b[35m'
	cyan      = reset + '\x1b[36m'
	Bold      = "\033[1m"
	underline = "\033[4m"

def find_method(method):
	try:
		return [{
			"delete": requests.delete,
			"get": requests.get,
			"head": requests.head,
			"patch": requests.patch,
			"post": requests.post,
			"put": requests.put
		}[method.lower().strip()], method]
	except:
		return [requests.head, "head"]

def randomString(n,text=""):
	# Randomization in recursion XD
	final = ''.join(str(random.choice(string.ascii_letters+string.digits)) for i in range(n))
	if text:
		final += "-"+text
	if len(final.split("-"))==(n-1):
		return final
	else:
		return randomString(n,final)

def wildcard_detector(url):
	responses = []
	u = url
	if not u.startswith("http"):
		u = "http://"+u
	if u.endswith("/"):
		u = u[:-1]
	for i in range(2): # check if two non-existent pages gives the same response
		u = u+"/"+randomString(6)
		try:
			req = requests.get(u, headers=headers, timeout=15)
			responses.append([req.status_code, req.text])
		except requests.exceptions.RequestException:
			return url
		except Exception as e:
			# Debug
			print(e)
			return url

	if responses[0][0]==responses[1][0]==404:
		return ""
	elif (responses[0][0]==responses[1][0]) and (responses[0][1]==responses[1][1]):
		return url

def checker(hosts, path, headers, request_method, request_timeout, follow_redirect, sleep, whitelist_codes, blacklist_codes):
	result = {}
	for url in hosts:
		if not url.startswith("http"):
			url = "http://"+url
		if url.endswith("/"):
			url = url[:-1]
		try:
			req = request_method(url+"/"+path, headers=headers, timeout=request_timeout, allow_redirects=follow_redirect)
		except requests.exceptions.RequestException:
			continue
		else:
			if req.status_code!=404:
				if whitelist_codes and req.status_code not in whitelist_codes:
					continue
				elif blacklist_codes and req.status_code in blacklist_codes:
					continue
				else:
					if url not in result.keys():
						result[url] = {}
					result[url][url+"/"+path] = {
						"status_code": req.status_code,
						"content_length": int(req.headers.get('content-length', 0)),
						"headers": dict(req.headers)
						# "response": req.text
					}
		time.sleep(sleep)
	return result

def main(cli):
	total_result = {}
	http_method,text_method = find_method(cli.method)
	threads, sleep, request_timeout, follow_redirect = cli.threads, cli.throttle, cli.timeout, cli.follow_redirects # Default: 100,0,10,False
	with open(cli.hosts) as h, open(cli.paths) as p:
		hosts = h.read().splitlines()
		paths = p.read().splitlines()
	if cli.headers:
		for line in cli.headers.split("\n"):
			if ":" not in line:
				print(color.red+" [!] Invalid headers! headers should be at the form (name:value) seperated by \\n.")
				exit(1)
			else:
				headers.update({line.split(":")[0]:line.split(":")[1]})
	print(f"\t\t     {color.magneta} - Loaded {len(hosts)} host(s) and {len(paths)} path(s) -{color.reset}")
	print(f"  {color.red} Threads: {threads} - HTTP method: {text_method.upper()} - Throttle: {sleep}s - Timeout: {request_timeout}s - Redirections: {str(follow_redirect)}{color.reset}\n")
	if not cli.all_hosts:
		futures, number = [], 0
		start = time.time()
		old = len(hosts)
		with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
			for host in hosts:
				number +=1
				sys.stdout.write("\r{}[+]{} First filtering websites with wilcard response in concurrent ({}/{})".format(color.green, color.reset, number,len(hosts) ))
				sys.stdout.flush()
				futures.append( executor.submit(wildcard_detector, host))
			for d in concurrent.futures.as_completed(futures):
				number +=1
				dumb = d.result()
				if dumb:#lol
					sys.stdout.write("\n\r | Filtered {}{}{}".format(color.Bold, dumb, color.reset))
					sys.stdout.flush()
					hosts.remove(dumb)
			del futures[:]
			print(f"\n{color.blue} |{color.reset} Filtered unwanted hosts (Gone from {old} to {len(hosts)}), filtering elapsed time {time.strftime('%H:%M:%S', time.gmtime(time.time()-start))}.\n |")

	futures, number = [], 0
	start = time.time()
	with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
		for path in paths:
			number +=1
			sys.stdout.write("\r{}[+]{} Now Fetching paths for all hosts in concurrent ({}/{})".format(color.green, color.reset, number,len(paths) ))
			sys.stdout.flush()
			futures.append( executor.submit(checker, hosts, path, headers, http_method, request_timeout, follow_redirect, sleep, cli.match_codes, cli.filter_codes))
			time.sleep(0.005)
		number = 0
		sys.stdout.write("\n\r | Collecting results (Total progress: {:.2f}%)".format((number/len(paths))*100))
		sys.stdout.flush()
		for site in concurrent.futures.as_completed(futures):
			number +=1
			sys.stdout.write("\r | Collecting results (Total progress: {:.2f}%)".format((number/len(paths))*100))
			sys.stdout.flush()
			path_result = site.result()
			for key in path_result:
				if key in total_result.keys():
					total_result[key].update(path_result[key])
				else:
					total_result.update(path_result)
		del futures[:]

	result_paths,rows = 0,[]
	for host in total_result.keys():
		result_paths += len(total_result[host])
		for path in total_result[host].keys():
			rows.append([path, total_result[host][path]["status_code"], total_result[host][path]["content_length"]])
	if cli.display:
		print(create_table(rows), flush=True)
	else:
		print(flush=True)

	sys.stdout.write(f"{color.blue} |{color.reset} Found {result_paths} path(s) in {len(total_result)} host(s)")
	sys.stdout.flush()
	if total_result:
		if cli.output:
			out = cli.output
		else:
			out = "output.json"
		with open(out, "w") as f:
			json.dump(total_result, f, indent=4, sort_keys=True)
		print(f"  [Written detailed json results to {out}]",end="", flush=True)

	print(f"\n{color.blue} |{color.reset} Total elapsed time {time.strftime('%H:%M:%S', time.gmtime(time.time()-start))}.\n")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='ffa.py')
	parser.add_argument("hosts", help="File of hosts/domains file to work with")
	parser.add_argument("paths", help="File of paths file to test on")
	parser.add_argument("-hh", "--headers", metavar="", help="Headers you want to add to requests(ex: 'Host: 127.0.0.1')")
	parser.add_argument("-m", "--method", metavar="", help="HTTP method (default: HEAD)")
	parser.add_argument("-c", "--threads", metavar="", help="The number of maximum concurrent threads to use (Default: 100)", type=int, default=100)
	parser.add_argument("-r","--follow-redirects", help="Follow redirects for all sent requests (Default: not allowed)", action="store_true", default=False)
	parser.add_argument("-d","--display", help="Display less detailed output in the terminal without much noise.", action="store_true", default=False)
	parser.add_argument("-a","--all-hosts", help="Don't check for wildcard responses, fetch all!", action="store_true")
	parser.add_argument("-t", "--timeout", metavar="", help="Request timeout for each single request (Default: 10)", type=float, default=10)
	parser.add_argument("-s", "--throttle", metavar="", help="Time to wait between each request (By default no throttling)", type=float, default=0)
	parser.add_argument("-mc", '--match-codes', metavar="", nargs='+', type=int, help="Whitelisting filter, returns results with given status codes (separated with space)",  default=[])
	parser.add_argument("-fc", '--filter-codes', metavar="", nargs='+', type=int, help="Blacklisting filter, don't return results with given status codes (separated with space)", default=[])
	parser.add_argument("-o", "--output", metavar="", help="JSON output file name.")
	args = parser.parse_args()
	print(f"\n\t\t{color.white}{color.Bold} (F)etch (F)or (A)ll - {color.green}{color.Bold}By: Karim 'D4Vinci' Shoair{color.reset}")
	main(args)
