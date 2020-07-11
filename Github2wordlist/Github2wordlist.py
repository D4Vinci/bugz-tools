import argparse, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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

def main(args):
	url = "https://api.github.com/repos/{}/{}/git/trees/master?recursive={}"
	recursion = 1
	if args.no_recursion:
		recursion = 0
	try:
		parse = args.repo.split("github.com/")[1].split("/")
		user  = parse[0]
		repo  = parse[1]
	except:
		print(color.red+" [!] Invalid github url! Example: Github2wordlist.py https://github.com/google/flax")
		exit(1)

	print(f"{color.green}[+]{color.reset} Collecting files from Github...")
	try:
		req  = requests.get(url.format(user, repo, recursion), verify=False)
		data = req.json()
	except Exception as e:
		print(e)
		print(color.red+" [!] Couldn't connect to github")
		exit(1)

	result = set()
	for path in data["tree"]:
		result.add(path["path"])
	result = sorted(result)

	print(f" | Found {len(result)} file(s)/directorie(s)")
	if result and args.o:
		with open(args.o, "w") as f:
			f.writelines([r+"\n" for r in result])
		print(f" | Written result to {args.o}")

	elif result and not args.o:
		for line in result:
			print(f" | {line}")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='Github2wordlist.py')
	parser.add_argument("repo", help="https link of the github repo you want to work on.")
	parser.add_argument("--no-recursion", help="Omit this parameter to prevent recursively returning objects or subtrees.", action="store_true")
	parser.add_argument("-o", help="The output path of the wordlist")
	args = parser.parse_args()
	print(f"\n\t{color.Bold} Github2wordlist - {color.blue}{color.Bold}By: Karim 'D4Vinci' Shoair{color.reset}\n")
	main(args)
