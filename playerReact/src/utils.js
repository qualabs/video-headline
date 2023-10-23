export function loadScript (url) {
    return new Promise((resolve, reject) => {
      // Add a script in the head.
      const script = document.createElement('script')
      script.type = 'text/javascript'
      script.src = url
      const tag = document.getElementsByTagName('head')[0].appendChild(script)
      tag.onload = resolve
      tag.onerror = reject
    })
  }

  export function checkBoolString (boolValue) {
    return boolValue && boolValue.toLowerCase() === 'true'
  }