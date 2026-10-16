INTERNET ---- FW ----+---- DMZ    : WEB (443 open)
                    |
                    +---- INSIDE : DB (3306 from WEB only)

FW policy:
  INTERNET -> WEB : TCP/443  permit
  INTERNET -> DB  : TCP/3306 deny
  WEB      -> DB  : TCP/3306 permit

