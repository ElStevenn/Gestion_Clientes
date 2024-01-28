console.log("Hello world!");
let apikey = 'rmpxCixzGRet81UnltZUBLdURHhnJy4QSltELa6HjU8=';
let ip = "185.254.206.129";


async function login(username, password) {
    try {
        const body_request = new URLSearchParams();
        body_request.append("username", username);
        body_request.append("password", password);
        
        const response = await fetch("http://inutil.top/token", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "api-key": apikey 
            },
            body: body_request
        });
        
        if (!response.ok) {
            document.getElementById('status_message').textContent = "User doesn't exists";
            document.getElementById('status_message').style = "color:red;"
            throw new Error(`HTTP error! Status: ${response.status}`);
           
        }

        const result = await response.json();
        document.getElementById('status_message').textContent = "User verified!";
        document.getElementById('status_message').style = "color:green;"

        return result;

    } catch (error) {
        console.error("An error occurred with login: ", error);
    }
}


async function whoAmi() {
    try {
        // Verify if the user is already logged
        const response = await fetch('http://inutil.top/whoami');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("An error occurred:", error);
        // Handle the error as needed, for example, return null or a custom error message
        return null;
    }
}




async function vadilate_token(token_beaber) {
    // Verify the token created
    try{
        let request_body;

        // Send a login to autenticate the user, credentials and check if tht user has the correct credentials
        
        request_body = {'token_beaber': token_beaber}
      
       
        console.log(request_body);
        
        const response = await fetch(`http://inutil.top/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'api-key': apikey
            },
            body: JSON.stringify(request_body),
            credentials: 'include'})
        
        return response.json();
        
    } catch(error) {
        console.error("An error ocurred with whoAmi: ", error)
        return null;
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    document.getElementById('button_login_submit').addEventListener('click', async function(event) {
        event.preventDefault();
    
        let username = document.getElementById('username').value;
        let password = document.getElementById('password').value;

        try {
            const response = await login(username, password);
            console.log(response);
            const token_beaber = response.access_token;
            
            const whoami_response = await vadilate_token(token_beaber);
            
            if (whoami_response){
                if(whoami_response.role == 'root'){
                    window.location.replace('http://inutil.top/apiconf');
                }else if(whoami_response.role == 'admin'){
                    window.location.replace('http://inutil.top/docs');
                }else if (whoami_response.role == 'user'){
                    window.location.replace('http://inutil.top/');
                }
            }

        } catch (e) {
            // Handle error, notify the client that there's an issue (e.g., wrong password or network error)
            console.error(e);
            const errorMessage = e.response ? e.response : "Login failed due to a network error.";
            document.getElementById('status_message').textContent = String(e); // Change this whenever I can
            document.getElementById('status_message').style = "color: #ad0014;";
        }
    });
});


async function main(){
    const whoami_response = await whoAmi();
    if(whoami_response){
        if (whoami_response['status'] == 'success'){
            document.getElementById('status_message').textContent = "User already verified!";
            document.getElementById('status_message').style = "color:green;";
        } 
    }   

}
main();

