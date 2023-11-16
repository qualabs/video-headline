const fs = require('fs');
const { spawnSync } = require('child_process');

const originalPackageJson = require('./package.json');

function isSshKeyAvailable() {
  try {

    fs.accessSync(`${process.env.HOME}/.ssh/id_rsa`, fs.constants.R_OK);
    // Check if the SSH key is valid by attempting to connect to GitHub
    spawnSync('ssh', ['-T', 'git@github.com'], { stdio: 'inherit' });
    console.log('Package.json updated successfully.');
    return true;
  } catch (error) {
    return false;
  }
}


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



