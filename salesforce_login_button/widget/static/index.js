/** @param {{ model: DOMWidgetModel, el: HTMLElement }} context */

function render({ model, el }) {
  const buttonText = model.get('button_text') ?? 'Log in to Salesforce';
  const button = document.createElement("button");
  button.textContent = buttonText;
  el.appendChild(button);

  const loginUrl = () => model.get('login_url');
  const domain = () => model.get('domain');
  // let popup;
  console.log('loginUrl: ', loginUrl());
  console.log('domain: ', domain());

  button.onclick = () => {
    console.log('postLoginUrl: ', loginUrl());
    console.log('postLoginUrl: ', loginUrl());
    console.log('postDomain: ', domain());
    // Set up an event listenter to receive the auth information from the
    // popup window
    window.addEventListener('message', (event) => {
      if (event.origin !== window.location.origin) {
        console.error('Origin not allowed: ', event.origin);
        return;
      }

      const token = event.data;
      model.set('token', token);
      model.set('connected', true);
      model.save_changes();

    }, { once: true });

    // Open the login URL in a new window
    window.open(loginUrl(), '_blank', 'width=400,height=400');
    // if (popup) {
    //   popup.close();
    // }
    // popup = window.open(loginUrl, '_blank', 'width=400,height=400');
  }
}

export default { render };