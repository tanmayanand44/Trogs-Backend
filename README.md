# Trogs-Backend
Backend repository for Trogs application for Oktane Hackathon.

### How to setup ?
  1) Clone this repo.  
  2) Download config.js into the cloned Backend folder from [here](https://send.firefox.com/download/dd1525fb8b6504f1/#le5vLtlkm4nrgnVXc6Ko7g)  
  3) Download config.ini into the cloned Worker folder from [here](https://send.firefox.com/download/3a24ba5df3ba0528/#HOEaruAARTwdf7qUyjrBiA)  
  4) Download config.env into the cloned DockerDBSetup folder from [here](https://send.firefox.com/download/d9f7ac316d9ec068/#414zkwjjcivZ6HGTl-5SAA).  
  5) Run 
  ```
    $ docker network create trogsNetwork  
  ```
  6) Then `cd` into DockerDBSetup folder and run `docker-compose up`  
  7) Then open a new terminal and cd back into the main folder and again run `docker-compose up`.   
  8) Setup Complete :thumbsup:  

### Usage: 

### Currently API's are not documented but you can see their example usage in test.sh file.  

**Overview**  
* From frontend an accessToken will be sent in Header of each request, then Authorization handler middleware as defined in auth.js file check if the request is valid and put the JWT of the user as returned by Okta in to req.jwt and similarly for email and uid.  
* We will be identifying a user by it's unique uid in our database.  
<hr>. 

**Without Frontend**  

* To test the backend API's we need a valid accessToken, to do that open the accessToken.html by creating a server in python by following these steps (first ensure either you are logged out of all Okta services or either perform the browser steps in Incognito Mode):  

1) On terminal run (from python2), run this in the folder containing the code: 
  ```sh
  $ python -m SimpleHTTPServer  
  ```  
  
2) Now open http://localhost:8000 in Incognito and open accessToken.html with Console of Browser open.  

3) Log into your Okta account, after logging in the accessToken will be logged in console. Copy that token and place it in accessToken variable in test.sh file.  

4) Install [httpie](https://github.com/jakubroztocil/httpie#2installation) on your system.  

4) Then you can manipulate test.sh to test different API's by changing the url and type of request. You can read the [docs](https://httpie.org/doc) of httpie for help.   

### TODO

=> Implement search API  
