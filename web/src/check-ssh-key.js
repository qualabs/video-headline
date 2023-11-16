// check-ssh-key.js
const fs = require('fs');
const { spawnSync } = require('child_process');

function isSshKeyAvailable() {
  try {
    spawnSync('ssh', ['-T', 'git@github.com'], { stdio: 'inherit' });
    console.log('SSH key is available.');
    return true;
  } catch (error) {
    console.log('SSH key is not available.');
    return false;
  }
}


module.exports = isSshKeyAvailable;