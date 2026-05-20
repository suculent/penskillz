# penskillz — capabilities overview

Pentesting skill library aggregated from upstream frameworks. **1430 skills** across **7 sources**. Load this skill once to learn what's available, then load specific skills by name as the engagement demands.

## How to use this index

Each skill below is loadable directly by its `name`. Skill names follow the pattern `<source-prefix>-<topic>` (e.g. `strix-sql-injection`, `ht-network-services-pentesting-pentesting-rdp`, `gtfobins-suid`). When the task matches a row in the **Intent → skill lookup** at the bottom, prefer the named skill over re-deriving the approach.

## gtfobins — 11 skills

Linux/Unix legit-binary abuse, grouped by technique (shell, file-read, file-write, suid, sudo, capabilities, library-load). Use when you have local code-exec on a Linux host and need to escalate.

| category | count | example skill names |
| --- | ---: | --- |
| bind-shell | 1 | `gtfobins-bind-shell` |
| command | 1 | `gtfobins-command` |
| download | 1 | `gtfobins-download` |
| file-read | 1 | `gtfobins-file-read` |
| file-write | 1 | `gtfobins-file-write` |
| inherit | 1 | `gtfobins-inherit` |
| library-load | 1 | `gtfobins-library-load` |
| privilege-escalation | 1 | `gtfobins-privilege-escalation` |
| reverse-shell | 1 | `gtfobins-reverse-shell` |
| shell | 1 | `gtfobins-shell` |
| upload | 1 | `gtfobins-upload` |

## hacktricks — 670 skills

Broad offsec wiki. Strongest for per-port network-services pentesting, Linux/Windows/macOS hardening, mobile reversing, binary exploitation, forensics. Use when you need depth Strix and IATT don't cover.

| category | count | example skill names |
| --- | ---: | --- |
| binary-exploitation | 99 | `ht-binary-exploitation-arbitrary-write-2-exec-aw2exec-got-plt`, `ht-binary-exploitation-arbitrary-write-2-exec-aw2exec-malloc-hook`, `ht-binary-exploitation-arbitrary-write-2-exec-aw2exec-sips-icc-profile`, `ht-binary-exploitation-arbitrary-write-2-exec-www2exec-atexit`, `ht-binary-exploitation-arbitrary-write-2-exec-www2exec-dtors-and-fini-array`, _+94 more_ |
| generic-hacking | 12 | `ht-generic-hacking-archive-extraction-path-traversal`, `ht-generic-hacking-brute-force`, `ht-generic-hacking-esim-javacard-exploitation`, `ht-generic-hacking-exfiltration`, `ht-generic-hacking-reverse-shells`, _+7 more_ |
| generic-methodologies-and-resources | 83 | `ht-generic-methodologies-and-resources-basic-forensic-methodology`, `ht-generic-methodologies-and-resources-basic-forensic-methodology-adaptixc2-config-extraction-and-ttps`, `ht-generic-methodologies-and-resources-basic-forensic-methodology-anti-forensic-techniques`, `ht-generic-methodologies-and-resources-basic-forensic-methodology-docker-forensics`, `ht-generic-methodologies-and-resources-basic-forensic-methodology-file-integrity-monitoring`, _+78 more_ |
| hardware-physical-access | 8 | `ht-hardware-physical-access-escaping-from-gui-applications`, `ht-hardware-physical-access-firmware-analysis`, `ht-hardware-physical-access-firmware-analysis-android-mediatek-secure-boot-bl2-ext-bypass-el3`, `ht-hardware-physical-access-firmware-analysis-bootloader-testing`, `ht-hardware-physical-access-firmware-analysis-firmware-integrity`, _+3 more_ |
| linux-hardening | 62 | `ht-linux-hardening-bypass-bash-restrictions`, `ht-linux-hardening-bypass-bash-restrictions-bypass-fs-protections-read-only-no-exec-distroless`, `ht-linux-hardening-bypass-bash-restrictions-bypass-fs-protections-read-only-no-exec-distroless-ddexec`, `ht-linux-hardening-freeipa-pentesting`, `ht-linux-hardening-linux-environment-variables`, _+57 more_ |
| macos-hardening | 82 | `ht-macos-hardening-macos-auto-start-locations`, `ht-macos-hardening-macos-red-teaming`, `ht-macos-hardening-macos-red-teaming-macos-keychain`, `ht-macos-hardening-macos-red-teaming-macos-mdm`, `ht-macos-hardening-macos-red-teaming-macos-mdm-enrolling-devices-in-other-organisations`, _+77 more_ |
| mobile-pentesting | 64 | `ht-mobile-pentesting-android-app-pentesting`, `ht-mobile-pentesting-android-app-pentesting-abusing-android-media-pipelines-image-parsers`, `ht-mobile-pentesting-android-app-pentesting-accessibility-services-abuse`, `ht-mobile-pentesting-android-app-pentesting-adb-commands`, `ht-mobile-pentesting-android-app-pentesting-android-anti-instrumentation-and-ssl-pinning-bypass`, _+59 more_ |
| network-services-pentesting | 108 | `ht-network-services-pentesting-10000-network-data-management-protocol-ndmp`, `ht-network-services-pentesting-1026-pentesting-rusersd`, `ht-network-services-pentesting-1080-pentesting-socks`, `ht-network-services-pentesting-1099-pentesting-java-rmi`, `ht-network-services-pentesting-11211-memcache`, _+103 more_ |
| reversing | 8 | `ht-reversing-common-api-used-in-malware`, `ht-reversing-reversing-tools-basic-methods`, `ht-reversing-reversing-tools-basic-methods-angr`, `ht-reversing-reversing-tools-basic-methods-angr-angr-examples`, `ht-reversing-reversing-tools-basic-methods-blobrunner`, _+3 more_ |
| todo | 37 | `ht-todo-android-forensics`, `ht-todo-burp-suite`, `ht-todo-cookies-policy`, `ht-todo-hardware-hacking`, `ht-todo-hardware-hacking-fault-injection-attacks`, _+32 more_ |
| windows-hardening | 107 | `ht-windows-hardening-active-directory-methodology`, `ht-windows-hardening-active-directory-methodology-abusing-ad-mssql`, `ht-windows-hardening-active-directory-methodology-acl-persistence-abuse`, `ht-windows-hardening-active-directory-methodology-acl-persistence-abuse-badsuccessor`, `ht-windows-hardening-active-directory-methodology-acl-persistence-abuse-shadow-credentials`, _+102 more_ |

## internal-all-the-things — 166 skills

Active Directory and internal-network attack catalogue: Kerberos (asreproast, kerberoasting, S4U, RBCD, delegation), ADCS ESC1-ESC15, lateral movement, post-ex, cloud, container, DB-pivot techniques.

| category | count | example skill names |
| --- | ---: | --- |
| active-directory | 71 | `iatt-active-directory-ad-adcs-certificate-services`, `iatt-active-directory-ad-adcs-esc`, `iatt-active-directory-ad-adcs-esc01`, `iatt-active-directory-ad-adcs-esc02`, `iatt-active-directory-ad-adcs-esc03`, _+66 more_ |
| cheatsheets | 10 | `iatt-cheatsheets-as-400`, `iatt-cheatsheets-escape-breakout`, `iatt-cheatsheets-hash-cracking`, `iatt-cheatsheets-liferay`, `iatt-cheatsheets-mimikatz-cheatsheet`, _+5 more_ |
| cloud | 37 | `iatt-cloud-aws-aws-access-token`, `iatt-cloud-aws-aws-cli`, `iatt-cloud-aws-aws-cognito`, `iatt-cloud-aws-aws-dynamodb`, `iatt-cloud-aws-aws-ec2`, _+32 more_ |
| command-control | 5 | `iatt-command-control-cobalt-strike`, `iatt-command-control-cobalt-strike-beacons`, `iatt-command-control-cobalt-strike-kits`, `iatt-command-control-metasploit`, `iatt-command-control-mythic` |
| containers | 2 | `iatt-containers-docker`, `iatt-containers-kubernetes` |
| databases | 5 | `iatt-databases-mssql-audit-checks`, `iatt-databases-mssql-command-execution`, `iatt-databases-mssql-credentials`, `iatt-databases-mssql-enumeration`, `iatt-databases-mssql-linked-database` |
| devops | 9 | `iatt-devops`, `iatt-devops-cicd-azure-devops`, `iatt-devops-cicd-buildkite`, `iatt-devops-cicd-circle-ci`, `iatt-devops-cicd-drone-ci`, _+4 more_ |
| methodology | 4 | `iatt-methodology-android-applications`, `iatt-methodology-bug-hunting-methodology`, `iatt-methodology-source-code-analysis`, `iatt-methodology-vulnerability-reports` |
| redteam | 23 | `iatt-redteam-access-clickfix`, `iatt-redteam-access-html-smuggling`, `iatt-redteam-access-initial-access`, `iatt-redteam-access-office-attacks`, `iatt-redteam-access-phishing`, _+18 more_ |

## lolbas — 15 skills

Windows signed-binary abuse, grouped by MITRE-aligned category (Execute, Download, Upload, ADS, AWL Bypass, UAC Bypass, Compile, Credentials, Reconnaissance). Use when operating in a constrained Windows host.

| category | count | example skill names |
| --- | ---: | --- |
| ads | 1 | `lolbas-ads` |
| awl-bypass | 1 | `lolbas-awl-bypass` |
| compile | 1 | `lolbas-compile` |
| conceal | 1 | `lolbas-conceal` |
| copy | 1 | `lolbas-copy` |
| credentials | 1 | `lolbas-credentials` |
| decode | 1 | `lolbas-decode` |
| download | 1 | `lolbas-download` |
| dump | 1 | `lolbas-dump` |
| encode | 1 | `lolbas-encode` |
| execute | 1 | `lolbas-execute` |
| reconnaissance | 1 | `lolbas-reconnaissance` |
| tamper | 1 | `lolbas-tamper` |
| uac-bypass | 1 | `lolbas-uac-bypass` |
| upload | 1 | `lolbas-upload` |

## mastg — 426 skills

OWASP Mobile Application Security Testing Guide — per-test playbooks across Android and iOS, organised by MASVS category (STORAGE, AUTH, CRYPTO, CODE, NETWORK, PLATFORM, RESILIENCE).

| category | count | example skill names |
| --- | ---: | --- |
| Document | 31 | `mastg-document`, `mastg-document-0x01-foreword`, `mastg-document-0x02a-frontispiece`, `mastg-document-0x02b-masvs-mastg-adoption`, `mastg-document-0x02c-acknowledgements`, _+26 more_ |
| best-practices | 37 | `mastg-best-practices`, `mastg-best-practices-mastg-best-0001`, `mastg-best-practices-mastg-best-0002`, `mastg-best-practices-mastg-best-0003`, `mastg-best-practices-mastg-best-0004`, _+32 more_ |
| techniques | 134 | `mastg-techniques-android-mastg-tech-0001`, `mastg-techniques-android-mastg-tech-0002`, `mastg-techniques-android-mastg-tech-0003`, `mastg-techniques-android-mastg-tech-0004`, `mastg-techniques-android-mastg-tech-0005`, _+129 more_ |
| tests | 92 | `mastg-tests-android-masvs-auth-mastg-test-0017`, `mastg-tests-android-masvs-auth-mastg-test-0018`, `mastg-tests-android-masvs-code-mastg-test-0002`, `mastg-tests-android-masvs-code-mastg-test-0025`, `mastg-tests-android-masvs-code-mastg-test-0026`, _+87 more_ |
| tests-beta | 132 | `mastg-tests-beta`, `mastg-tests-beta-android-masvs-auth-mastg-test-0326`, `mastg-tests-beta-android-masvs-auth-mastg-test-0327`, `mastg-tests-beta-android-masvs-auth-mastg-test-0328`, `mastg-tests-beta-android-masvs-auth-mastg-test-0329`, _+127 more_ |

## payloads-all-the-things — 105 skills

Payload library complementing Strix. Use when you need raw payload variants / WAF bypass strings for a vulnerability class — XSS, SSRF, SSTI, NoSQLi, LFI, command injection, CSV/CRLF/header injection, etc.

| category | count | example skill names |
| --- | ---: | --- |
| API Key Leaks | 2 | `patat-api-key-leaks`, `patat-api-key-leaks-iis-machine-keys` |
| Account Takeover | 2 | `patat-account-takeover`, `patat-account-takeover-mfa-bypass` |
| Brute Force Rate Limit | 1 | `patat-brute-force-rate-limit` |
| Business Logic Errors | 1 | `patat-business-logic-errors` |
| CORS Misconfiguration | 1 | `patat-cors-misconfiguration` |
| CRLF Injection | 1 | `patat-crlf-injection` |
| CSS Injection | 1 | `patat-css-injection` |
| CSV Injection | 1 | `patat-csv-injection` |
| CVE Exploits | 2 | `patat-cve-exploits`, `patat-cve-exploits-log4shell` |
| Clickjacking | 1 | `patat-clickjacking` |
| Client Side Path Traversal | 1 | `patat-client-side-path-traversal` |
| Command Injection | 1 | `patat-command-injection` |
| Cross-Site Request Forgery | 1 | `patat-cross-site-request-forgery` |
| DNS Rebinding | 1 | `patat-dns-rebinding` |
| DOM Clobbering | 1 | `patat-dom-clobbering` |
| Denial of Service | 1 | `patat-denial-of-service` |
| Dependency Confusion | 1 | `patat-dependency-confusion` |
| Directory Traversal | 1 | `patat-directory-traversal` |
| Encoding Transformations | 1 | `patat-encoding-transformations` |
| External Variable Modification | 1 | `patat-external-variable-modification` |
| File Inclusion | 3 | `patat-file-inclusion`, `patat-file-inclusion-lfi-to-rce`, `patat-file-inclusion-wrappers` |
| Google Web Toolkit | 1 | `patat-google-web-toolkit` |
| GraphQL Injection | 1 | `patat-graphql-injection` |
| HTTP Parameter Pollution | 1 | `patat-http-parameter-pollution` |
| Headless Browser | 1 | `patat-headless-browser` |
| Hidden Parameters | 1 | `patat-hidden-parameters` |
| Insecure Deserialization | 7 | `patat-insecure-deserialization`, `patat-insecure-deserialization-dotnet`, `patat-insecure-deserialization-java`, `patat-insecure-deserialization-node`, `patat-insecure-deserialization-php`, _+2 more_ |
| Insecure Direct Object References | 1 | `patat-insecure-direct-object-references` |
| Insecure Management Interface | 1 | `patat-insecure-management-interface` |
| Insecure Randomness | 1 | `patat-insecure-randomness` |
| Insecure Source Code Management | 5 | `patat-insecure-source-code-management`, `patat-insecure-source-code-management-bazaar`, `patat-insecure-source-code-management-git`, `patat-insecure-source-code-management-mercurial`, `patat-insecure-source-code-management-subversion` |
| JSON Web Token | 1 | `patat-json-web-token` |
| Java RMI | 1 | `patat-java-rmi` |
| LDAP Injection | 1 | `patat-ldap-injection` |
| LaTeX Injection | 1 | `patat-latex-injection` |
| Mass Assignment | 1 | `patat-mass-assignment` |
| NoSQL Injection | 1 | `patat-nosql-injection` |
| OAuth Misconfiguration | 1 | `patat-oauth-misconfiguration` |
| ORM Leak | 1 | `patat-orm-leak` |
| Open Redirect | 1 | `patat-open-redirect` |
| Prompt Injection | 1 | `patat-prompt-injection` |
| Prototype Pollution | 1 | `patat-prototype-pollution` |
| Race Condition | 1 | `patat-race-condition` |
| Regular Expression | 1 | `patat-regular-expression` |
| Request Smuggling | 1 | `patat-request-smuggling` |
| Reverse Proxy Misconfigurations | 1 | `patat-reverse-proxy-misconfigurations` |
| SAML Injection | 1 | `patat-saml-injection` |
| SQL Injection | 10 | `patat-sql-injection`, `patat-sql-injection-bigquery-injection`, `patat-sql-injection-cassandra-injection`, `patat-sql-injection-db2-injection`, `patat-sql-injection-mssql-injection`, _+5 more_ |
| Server Side Include Injection | 1 | `patat-server-side-include-injection` |
| Server Side Request Forgery | 3 | `patat-server-side-request-forgery`, `patat-server-side-request-forgery-ssrf-advanced-exploitation`, `patat-server-side-request-forgery-ssrf-cloud-instances` |
| Server Side Template Injection | 8 | `patat-server-side-template-injection`, `patat-server-side-template-injection-asp`, `patat-server-side-template-injection-elixir`, `patat-server-side-template-injection-java`, `patat-server-side-template-injection-javascript`, _+3 more_ |
| Tabnabbing | 1 | `patat-tabnabbing` |
| Type Juggling | 1 | `patat-type-juggling` |
| Upload Insecure Files | 2 | `patat-upload-insecure-files`, `patat-upload-insecure-files-configuration-apache-htaccess` |
| Virtual Hosts | 1 | `patat-virtual-hosts` |
| Web Cache Deception | 1 | `patat-web-cache-deception` |
| Web Sockets | 1 | `patat-web-sockets` |
| XPATH Injection | 1 | `patat-xpath-injection` |
| XS-Leak | 1 | `patat-xs-leak` |
| XSLT Injection | 1 | `patat-xslt-injection` |
| XSS Injection | 6 | `patat-xss-injection`, `patat-xss-injection-1-xss-filter-bypass`, `patat-xss-injection-2-xss-polyglot`, `patat-xss-injection-3-xss-common-waf-bypass`, `patat-xss-injection-4-csp-bypass`, _+1 more_ |
| XXE Injection | 1 | `patat-xxe-injection` |
| Zip Slip | 1 | `patat-zip-slip` |
| _LEARNING_AND_SOCIALS | 3 | `patat-learning-and-socials-books`, `patat-learning-and-socials-twitter`, `patat-learning-and-socials-youtube` |

## strix — 37 skills

Authoritative web/API methodology. Frontmatter-authored playbooks for SQLi, XSS, SSRF, SSTI, IDOR, RCE, GraphQL, mass-assignment, business logic, race conditions, plus tooling syntax (nmap, sqlmap, ffuf, nuclei, httpx, ...).

| category | count | example skill names |
| --- | ---: | --- |
| cloud | 1 | `strix-kubernetes` |
| custom | 1 | `strix-source-aware-sast` |
| frameworks | 3 | `strix-fastapi`, `strix-nestjs`, `strix-nextjs` |
| protocols | 1 | `strix-graphql` |
| technologies | 2 | `strix-firebase-firestore`, `strix-supabase` |
| tooling | 9 | `strix-ffuf`, `strix-httpx`, `strix-katana`, `strix-naabu`, `strix-nmap`, _+4 more_ |
| vulnerabilities | 20 | `strix-authentication-jwt`, `strix-broken-function-level-authorization`, `strix-business-logic`, `strix-csrf`, `strix-header-injection`, _+15 more_ |

## Intent → skill lookup

| Want to do... | Load |
| --- | --- |
| Web vuln testing (SQLi/XSS/SSRF/SSTI/IDOR/RCE/...) | `strix-<class>, patat-<class>` |
| GraphQL or REST API hardening | `strix-graphql, strix-mass-assignment, strix-broken-function-level-authorization` |
| JWT / OIDC token attacks | `strix-authentication-jwt` |
| Kubernetes / container security | `strix-kubernetes, ht-linux-hardening-*` |
| Active Directory + Kerberos | `iatt-active-directory-*, ht-windows-hardening-*` |
| ADCS certificate-services abuse (ESC1..ESC15) | `iatt-active-directory-ad-adcs-esc*` |
| Per-port network-services pentest | `ht-network-services-pentesting-pentesting-<service>` |
| Linux privilege escalation via legit binaries | `gtfobins-suid, gtfobins-sudo, gtfobins-capabilities, gtfobins-shell` |
| Linux post-ex shell / file IO | `gtfobins-shell, gtfobins-file-read, gtfobins-file-write` |
| Windows execution / persistence via signed binaries | `lolbas-execute, lolbas-awl-bypass, lolbas-uac-bypass, lolbas-ads` |
| Windows download / exfil via LOLBAS | `lolbas-download, lolbas-upload` |
| Android app testing (storage/crypto/auth/network) | `mastg-tests-android-masvs-<category>-*` |
| iOS app testing | `mastg-tests-ios-masvs-<category>-*` |
| Subdomain / asset recon | `strix-subfinder, strix-httpx, strix-katana, strix-naabu` |
| Nmap / port scanning | `strix-nmap, strix-naabu` |
| Source-aware SAST | `strix-source-aware-sast, strix-semgrep` |
| File upload + path traversal exploitation | `strix-insecure-file-uploads, strix-path-traversal-lfi-rfi, patat-file-inclusion` |
| Subdomain takeover | `strix-subdomain-takeover` |
| Open redirect / CSRF / header injection | `strix-open-redirect, strix-csrf, strix-header-injection` |

Patterns with `<class>`, `<category>`, `<service>` are placeholders — substitute the relevant term and try the matching skill name (e.g. `strix-sql-injection`, `ht-network-services-pentesting-pentesting-smb`, `mastg-tests-android-masvs-storage-mastg-test-0001`).
