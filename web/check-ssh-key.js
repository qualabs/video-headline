const fs = require('fs');
const { execSync } = require('child_process');

function isSshKeyAvailable() {
  try {
    fs.accessSync(`${process.env.HOME}/.ssh/id_rsa`, fs.constants.R_OK);
    execSync('ssh -T git@github.com', { stdio: 'ignore' });

    return true;
  } catch (error) {
    return false;
  }
}

const originalPackageJson = require('./package.json');

const updatedPackageJson = {
  ...originalPackageJson,
  dependencies: {
    ...originalPackageJson.dependencies,
    ...(isSshKeyAvailable()
      ? { 'video-headline-fast-channels': 'git@github.com:qualabs/video-headline-fast-channels.git' }
      : {})
  }
};


fs.writeFileSync('package.json', JSON.stringify(updatedPackageJson, null, 2));
console.log('Package.json updated successfully.');
