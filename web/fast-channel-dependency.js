// check-ssh-key.js
const fs = require('fs');
const isSshKeyAvailable = require('./src/check-ssh-key'); 

const originalPackageJson = require('./package.json');
const updatedPackageJson = {
  ...originalPackageJson,
  dependencies: {
    ...originalPackageJson.dependencies,
    ...(isSshKeyAvailable()
      ? { 'video-headline-fast-channels': 'git+ssh://git@github.com:qualabs/video-headline-fast-channels.git#hotfix/add-package-json'
    } 
      : {})
  }
};

fs.writeFileSync('package.json', JSON.stringify(updatedPackageJson, null, 2));
