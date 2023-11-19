const { spawnSync } = require('child_process');

function isSshKeyAvailable() {
  try {
    const result = spawnSync('ssh', ['-T', 'git@github.com']);
    if (result.status === 1) {
      console.log('SSH key is available.');
      return true;
    } else {
      console.log('SSH key is not available.');
      return false;
    }
  } catch (error) {
    console.log('SSH key is not available.', error);
    return false;
  }
}

module.exports = isSshKeyAvailable;