# create admin user  

```
docker run --rm -v `pwd`/manictime/Data:/app/Data --entrypoint dotnet  manictime/manictimeserver ManicTimeServer.dll addadmin -u admin@example.com -p password4321
```

# run local testing server

```
docker run --rm -v `pwd`/manictime/Data:/app/Data -p 8080:8080 manictime/manictimeserver
```
