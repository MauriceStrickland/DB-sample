## Mail Detection
### Background
There is a certain tool that lacks a logging functionality other than email. The email list  the "logs" are sent to is limited to just a handful of users. In order to share the "logs" to a wider audience there was a need to put these logs somewhere they can be accessed easily.

### High-Level Approach 
Since email was the only source I decided to query a user's email for these messages using a nice library for exchange interactions. Then I parse the emails for specific details and send that information to an API (I also wrote this) for storage.

This script was written to address a gap in compliance and has served as a stop gap to a tool that needs major improvements.
## Perforce User Management
### Background
This requirements for this project was to write a script that would find users that have an active account in the Perforce VCS but have left the company. Since this VCS tool had a first come first serve license setup, there was a tendency for licenses to be assigned to users that have departed (this was before SSO).

### High-Level Approach
Since this VCS had a python library that guided the decision to write it in python. This script was split into a few specific classes to keep the code readable. The main module (perforce_user_management) served as the driver and entry point to the script. It instantiated the classes connected to LDAP server and then to the VCS to do the processing. Once a "departed" list was created, depending on the mode, those users would be removed and the licenses would be free once again. To end the script an email would be sent to the admins of the tool describing which users were removed.

## Report Scrape
### Background
This script was created because of a need and guided by constraints. For an excel based forecasting tool (which I developed) users wanted to see this report right in excel and get updates at the click of a button. However getting data out of OBIEE programmatically was challenging. Mainly because the tool admins where not handing out api access. So I decided to take a creative approach and scrape the website to get this data out and into a database that users can access easily. 

### High-Level Approach
Use selenium to open the webpage and login. Once in, navigate to the report based off the name. Once the report is selected wait for it to populate then download it to disk for post-processing. At each step, the script will ensure the page is fully loaded before proceeding.