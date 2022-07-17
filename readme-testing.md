# create admin user  

```
docker run --rm -v `pwd`/manictime/Data:/app/Data --entrypoint dotnet  manictime/manictimeserver ManicTimeServer.dll addadmin -u admin@example.com -p password4321
```

# run local testing server

```
docker run --name manic_test --rm -v `pwd`/manictime/Data:/app/Data -p 8090:8080 manictime/manictimeserver
```
