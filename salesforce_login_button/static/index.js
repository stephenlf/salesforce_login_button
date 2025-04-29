/** @param {{ model: DOMWidgetModel, el: HTMLElement }} context */

function render({ model, el }) {
  const buttonText = model.get('button_text') ?? 'Log in to Salesforce';
  const loginUrl = model.get('login_url');

  const button = document.createElement("button");
  button.textContent = buttonText;
  el.appendChild(button);

  button.onclick = () => {
    // Open up the login URL in a new 
    window.open(loginUrl, '_blank', 'width=400,height=400');
    window.addEventListener('message', (event) => {
      if (event.origin !== window.location.origin) {
        console.error('Origin not allowed: ', event.origin);
        return;
      }

      console.log('Received auth message: ', event.data);

      model.set('auth_response', event.data);
    }, { once: true });
  }
}

export default { render };