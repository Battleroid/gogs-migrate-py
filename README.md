# gogs-migrate-py

Script to migrate repositories from Github to Gogs installation.

### Usage

Name | Description
---- | -----------
`new_config` | Generate new configuration file with filename.
`migrate` | Migrate repositories with information in given configuration file.

### How To

##### Github

* You will need to generate a personal OAuth token for retrieving information on repos.
* That's pretty much it for Github.

##### Gogs

* You'll need the API URL for your Gogs installation
* You'll need the URL for pushing repositories to your Gogs installation (I kept it like this so you can make use of the shorthand definitions you may have in `~/.ssh/config`)
* You'll need a access token (Your Settings > Applications)

That's pretty much it. The fabric script will try its best to grab all repositories from Github that you are the owner of or have pull permissions iirc.
