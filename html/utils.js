// utils.js

export function displayUserMessage(responseDiv, message) {
    const userMessage = document.createElement('div');
    userMessage.className = 'message user';
    userMessage.textContent = message;
    responseDiv.appendChild(userMessage);
    responseDiv.scrollTop = responseDiv.scrollHeight;
}

export function addSpinner(responseDiv) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.role = 'status';
    const spinnerSpan = document.createElement('span');
    spinnerSpan.className = 'visually-hidden';
    spinnerSpan.textContent = 'Loading...';
    spinner.appendChild(spinnerSpan);
    responseDiv.appendChild(spinner);
    return spinner;
}

export function removeSpinner(responseDiv, spinner) {
    responseDiv.removeChild(spinner);
}

export function displayAssistantMessage(responseDiv, message, isStreaming = false) {
    let assistantMessage = document.createElement('div');
    assistantMessage.className = 'message assistant';
    if (isStreaming) {
        assistantMessage.innerText = message;
    } else {
        assistantMessage.textContent = message;
    }
    responseDiv.appendChild(assistantMessage);
    responseDiv.scrollTop = responseDiv.scrollHeight;
    return assistantMessage;
}

export function handleError(responseDiv, error) {
    const errorMessage = document.createElement('div');
    errorMessage.className = 'message error';
    errorMessage.textContent = `Error: ${error.message}`;
    responseDiv.appendChild(errorMessage);
}
