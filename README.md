# MySQL API in Python 

Using the aiomysql (aiomysql is a "driver" for accessing a MySQL database from the asyncio (PEP-3156/tulip) framework, and it depends on and reuses most parts of PyMySQL) and FastAPI framework.

Simplify your API experience with this single-file main.py solution, featuring seamless and free MySQL integration for efficient database management.

# MySQL Structure

This is a hypothetical example of a Webhook to API service. In this scenario, we will be developing the API that retrieves and inserts data to our MySQL database. The webhook system for this example is operating in a separate environment from the MySQL database. To facilitate understanding, we have three tables: Users (tbluser), Webhooks (tblwhid), and Webhook Contents (tblwh). Their structures are outlined below.

### Users - tbluser

CREATE TABLE  `tbluser` ( 

    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,

    `email` varchar(45) NOT NULL,

    `phone` varchar(45) NOT NULL,  

    `token` varchar(45) NOT NULL,

    `status` tinyint(3) unsigned NOT NULL DEFAULT '0',
    
    `pwd` varchar(45) NOT NULL,

    PRIMARY KEY (`id`)

) ENGINE=InnoDB DEFAULT CHARSET=latin1;

### Webhooks - tblwhid

CREATE TABLE  `tblwhid` (

    `id` int(10) unsigned NOT NULL DEFAULT '0',

    `user_id` int(10) unsigned NOT NULL,

    `wh_url` varchar(255) NOT NULL,

    `wh_name` varchar(45) NOT NULL,

    `status` tinyint(1) NOT NULL,

    PRIMARY KEY (`id`)

) ENGINE=InnoDB DEFAULT CHARSET=latin1;

### Webhook Contents - tblwh

CREATE TABLE  `tblwh` (

    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,

    `content` longtext NOT NULL,

    `ip` varchar(15) NOT NULL,

    `api` tinyint(1) NOT NULL,

    `dt` varchar(30) NOT NULL,

    `user_id` int(10) unsigned NOT NULL,

    `wh_id` int(10) unsigned NOT NULL,

    PRIMARY KEY (`id`)

) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1;

# How it works

Our service's users don't need to set up their own webhook servers to integrate with services such as Twilio for WhatsApp, Stripe for payment processing, or Active Campaign for marketing automation. Instead, they can use our service to receive webhook content and make periodic API calls from their non-public servers or computers to retrieve the information.

Assuming the webhook system is already running and inserting content directly into a MySQL database in a production environment, we will use two Python frameworks, FastAPI to set up the server and aiomysql to manipulate the data, to build the API system that retrieves information. FastAPI's native SQLalchemy support is limited in a hybrid environment like this, where we need to manipulate MySQL with more flexibility within the solution.

We will also use Basic Authentication with a username and password to authenticate users in API calls. However, another application manages the users table, and users can access a hypothetical web dashboard with their email and password. For API Basic Authentication, we will use the numeric user code as the API Basic Auth username and a system-generated 32-character alphanumeric token as the API Basic Auth password. The authentication for API calls will follow the Basic schema of Base64 encryption of the concatenated string of username:token.

# Customization

We have developed a personalized documentation environment that includes examples for each API call. Additionally, users can verify their API authentication by making a call that retrieves only their username, which also serves as an input parameter for the call.

# Minimal Approach

By using a single file, main.py, our project is more concise and easier to comprehend. The authentication and data manipulation processes are straightforward and intentionally designed to be easily readable and usable. Modifications can be made with minimal effort and quickly applied to a production environment.

