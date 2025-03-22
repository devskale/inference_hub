
function decodeJWT(token) {
  try {
    const [headerB64, payloadB64, signature] = token.split(".");

    const header = JSON.parse(
      atob(headerB64.replace(/-/g, "+").replace(/_/g, "/"))
    );
    const payload = JSON.parse(
      atob(payloadB64.replace(/-/g, "+").replace(/_/g, "/"))
    );

    return {
      header,
      payload,
      signature,
    };
  } catch (error) {
    return { error: "Failed to decode JWT", details: error.message };
  }
}

async function handleLoginOld() {
  const resultDiv = document.getElementById("resultLogin");
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    // Using relative path since we're on the same domain
    const response = await axios.post(
      "http://pind.mooo.com:8000/files/api/login",
      {
        username,
        password,
      }
    );

    const token = response.data;
    const decoded = decodeJWT(token);

    // Store token
    localStorage.setItem("filebrowser_token", token);
    localStorage.setItem(
      "filebrowser_token_saved_at",
      new Date().toISOString()
    );

    // Display result
    resultDiv.innerHTML = `<pre>
Token Retrieved Successfully! expires ${new Date(
      decoded.payload.exp * 1000
    ).toLocaleString()}


Token will expire: ${new Date(decoded.payload.exp * 1000).toLocaleString()}
</pre>`;
  } catch (error) {
    const message = error.response
      ? `Server Error: ${error.response.status} - ${JSON.stringify(
          error.response.data
        )}`
      : `Error: ${error.message}`;

    resultDiv.innerHTML = `<div class="error">${message}</div>`;
  }
}

// Check for existing token on load
window.onload = () => {
    const token = localStorage.getItem("filebrowser_token");
    const resultDiv = document.getElementById("resultLogin");

    if (token) {
        const decoded = decodeJWT(token);
        if (decoded && decoded.payload && decoded.payload.exp) {
            const expiryDate = new Date(decoded.payload.exp * 1000);
            if (expiryDate > Date.now()) {
                resultDiv.innerHTML = `<pre>
Existing Token Found, expires ${expiryDate.toLocaleString()}: 

</pre>`;
                return; // Exit early if valid token found
            }
        }
        // If we reach here, either decode failed, no payload or no valid expiry.
        resultDiv.innerHTML = "<p>No valid token found.</p>";
    } else {
        resultDiv.innerHTML = "<p>No valid token found.</p>";
    }
};
