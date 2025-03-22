// filebrowser.js
import config from './config.js';

const resultLoginDiv = document.getElementById('resultLogin');
const fileListDiv = document.getElementById('fileList'); // Get the file list div
let isLoggedIn = true;

window.handleLogin = async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const loginUrl = `https://skaledev-loginfilebrowser.web.val.run?user=${encodeURIComponent(username)}&pw=${encodeURIComponent(password)}`;

    try {
        const response = await axios.get(loginUrl);
        console.log("Full response:", response);

        if (response.status === 200) {
            const responseData = response.data;

            if (responseData && responseData.loginStatus === "loginOK") {
                console.log("Login successful!", responseData);
                console.log("Cookie expiration time:", responseData.expiresAt);
                resultLoginDiv.textContent = `Login successful. Cookie expires at: ${responseData.expiresAt}`;

                isLoggedIn = true;
                 // Call listdir function when login is ok
                 handleListDir();


            } else {
                resultLoginDiv.textContent = "Login failed. Invalid credentials";
                console.error("Login failed", responseData);
            }
        } else {
            resultLoginDiv.textContent = `Login failed. Status: ${response.status}`;
            console.error("Login failed", response.status, response.data);
        }
    } catch (error) {
        resultLoginDiv.textContent = `Login failed due to an error: ${error}`;
        console.error("Login failed due to an error:", error);
    }
};


window.handleListDir = async () => {
     if(!isLoggedIn){
        console.warn("User is not logged in. Cannot list directory.")
        return;
     }

    const user = document.getElementById('username').value;
    const dir = document.getElementById('directory').value;
    const listDirUrl = `https://skaledev-dirfilebrowser.web.val.run/?user=${encodeURIComponent(user)}&dir=${encodeURIComponent(dir)}`;

    try {
        const response = await axios.get(listDirUrl);

        if (response.status === 200) {
          const responseData = response.data;
            console.log("ListDir response:", responseData);

            // Display file list
           renderFileList(responseData.items);


        } else {
           fileListDiv.textContent = `Failed to load directory. Status: ${response.status}`;
            console.error("ListDir failed", response.status, response.data);
        }
    } catch (error) {
      fileListDiv.textContent = `Failed to load directory due to an error: ${error}`;
       console.error("ListDir failed due to an error:", error);
    }
};

function renderFileList(items){
  fileListDiv.innerHTML = '';  // Clear previous list

    if(items && items.length > 0){
        const list = document.createElement('ul');

        items.forEach(item => {
           const listItem = document.createElement('li');
           listItem.textContent = `${item.name} (Size: ${item.size} bytes, Modified: ${item.modified})`;
            list.appendChild(listItem);
        });
         fileListDiv.appendChild(list);

    } else {
       fileListDiv.textContent = "No files found in the directory.";
    }

}

