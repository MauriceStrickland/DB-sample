## Mail Detection
### Background
There is a certain tool that lacks a logging functionality (other than email). The email list that the "logs" are sent to is limited to only a handful of users. In order to share the "logs" with a wider audience, there was a need for them to exist where they could be easily accessed.

### High-Level Approach 
Since email was the only source, I decided to query a user's email for these messages using a helpful library for Exchange interactions, parse the emails for specific details, and send that information to an API (I also wrote this) for storage.

This script was written to address a gap in compliance and has served as a stop-gap to a tool that needs major improvements.
## Perforce User Management
### Background
The requirements for this project were to write a script that would find users who have an active account in the Perforce VCS but have left the company. Since this VCS tool has a "first-come, first-serve" license setup, there is a tendency for licenses to be assigned to users that have departed (this was before SSO).

### High-Level Approach
This script was split into a few specific classes to keep the code clean and legible. The main module (perforce_user_management) served as the driver and entry point to the script. It instantiated the classes, connected to a LDAP server, and then to the VCS to do the processing. Once a "departed" list was created, depending on the mode, those users would be removed and the licenses would be free once again. To end the script, an email would be sent to the admins of the tool describing which users were removed.

## Report Scrape
### Background
This script was created because of a need and guided by constraints. For an excel-based forecasting tool (which I developed) users wanted to see this report directly in excel and receive updates at the click of a button. However, getting data out of OBIEE programmatically is challenging. Mainly because the tool admins where not handing out API access. So I decided to take a creative approach and scrape the website in order to get this data out of OBIEE and into a database that users can easily access. 

### High-Level Approach
Use Selenium to open the webpage and login. Once logged in, navigate to the report based off the name. Once the report is selected, wait for it to populate, then download it to the disk for post-processing. At each step, the script will ensure the page is fully loaded before proceeding.
