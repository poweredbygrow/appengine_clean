# appengine_clean
Clean up old versions of AppEngine instances to avoid the dreaded "Your app may not have more than 210 versions. Please delete one of the existing versions before trying to create a new version" error

## Usage:

First, let's do a dry-run. Run the following to keep 15 versions of each module around:
```
appengine-clean my-project-id 15 --dry-run
```

If you're happy with the result of the dry-run, let's delete:

```
appengine-clean my-project-id 15 --force
```

