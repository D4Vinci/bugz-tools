# (F)etch (F)or (A)ll
A very customizable tool for fetching many paths for many hosts/domains very fast using concurrency without much stress on hosts/domains.

- **How it work?**

FFA takes a list of hosts/domains and list of paths (in any format) then checks the given targets for wild-card responses to save time then loops over the given paths and fetch every target with the current path then finally saves the status code, content length and response headers for each path in JSON file and display this result if you want without headers!

- **How far FFA is customizable?**

If you look in the command-line arguments bellow, you would notice that you can specify a custom HTTP headers, set HTTP method, set HTTP request timeout, choose to follow redirections or not, set a time to sleep between requests if there's rate-limiting, and finally you can filter results by status code. It does all of that and still faster than others!

- **ًWhat's wild-card responses and how FFA tests for it?**

Wild-card response is when a website gives the same response (Not 404 one) for any tested path. Testing wordlists on these kind of websites could be a waste of time as the website could return code 200 for any tested endpoints! FFA detects these websites by generating a two completely random endpoints then test it on the same website so if website didn't return 404 on any of them and it returns the same status codes for both endpoints and the same exact response, FFA tells this website have a wildcard response and don't test paths on it which saves a lot of time.

# Screenshots
<table>
  <tr>
  <th>Test</th>
    <th><center>⚡ <b>FFA against (36*6101) URL to fetch</b> ⚡ </center></th>
    <th><center>⚡ <b>FFA against (36*63) URL to fetch</b> ⚡</center></th>
  </tr>
  <tr>
  <th>POC</th>
    <td><img src="Screenshot1.png"></td>
    <td><img src="Screenshot2.png"></td>
    <!-- Wanted to put a picture of meg to compare ahahahaa-->
  </tr>
  <tr>
  <th>Time</th>
    <td><center><b>27 Minutes</b></center></td>
    <td><center><b>34 Seconds</center></b></td>
  </tr>
</table>

## Basic Usage
Given a file full of paths (if endpoint begins with a slash, it's removed then re-added when fetching so you can put in any format):

```
/robots.txt
sitemap.xml
crossdomain.xml
```
And a file full of hosts (If a host doesn't start with http, FFA will automatically adds http:// to the host while fetching):

```
https://example.com
sub.google.com
sub.example.net
```
You can fetch them all like bellow:
`python3 ffa.py hosts_file paths_file`

## Detailed Usage
```
ffa.py [-h] [-hh] [-m] [-c] [-r] [-d] [-a] [-t] [-s] [-mc  [...]] [-fc  [...]] [-o] hosts paths

positional arguments:
  hosts                 File of hosts/domains file to work with
  paths                 File of paths file to test on

optional arguments:
  -h,  --help                  show this help message and exit
  -hh, --headers               Headers you want to add to requests(ex: 'Host: 127.0.0.1')
  -m,  --method                HTTP method (default: HEAD)
  -c,  --threads               The number of maximum concurrent threads to use (Default: 100)
  -r,  --follow-redirects      Follow redirects for all sent requests (Default: not allowed)
  -d,  --display               Display less detailed output in the terminal without much noise.
  -a,  --all-hosts             Don't check for wildcard responses, fetch all!
  -t,  --timeout               Request timeout for each single request (Default: 10)
  -s,  --throttle              Time to wait between each request (By default no throttling)
  -mc, --match-codes  [...]    Whitelisting filter, returns results with given status codes (separated with space)
  -fc, --filter-codes [...]    Blacklisting filter, don't return results with given status codes (separated with space)
  -o,  --output                JSON output file name.
```

## Requirements
- Python 3.6+
- terminaltables module `pip3 install terminaltables`
