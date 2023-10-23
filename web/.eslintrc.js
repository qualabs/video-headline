module.exports = {
    "env": {
        "browser": true,
        "node": true,
        "es6": true,
        "jest/globals": true
    },
    "extends": [
      "eslint:recommended",
      "plugin:flowtype/recommended",
      "plugin:jest/recommended"
    ],
    "parserOptions": {
        "ecmaFeatures": {
            "experimentalObjectRestSpread": true,
            "jsx": true
        },
        "sourceType": "module"
    },
    "plugins": [
        "react",
        "flowtype",
        "jest"
    ],
    "rules": {
        "indent": ["error", 2, {
          "SwitchCase": 1
        }],
        "linebreak-style": ["error", "unix"],

        "semi": ["error", "never"],
        "quotes": ["error", "single", {
          "avoidEscape": true,
          "allowTemplateLiterals": true
        }],
        "jsx-quotes": ["error", "prefer-single"],

        "brace-style": ["error", "1tbs", {"allowSingleLine": true}],
        "space-before-function-paren": "error",
        "space-before-blocks": "error",
        "arrow-spacing": "error",
        "keyword-spacing": ["error"],
        "no-multi-spaces": ["error", {ignoreEOLComments: true}],
        "comma-spacing": ["error", {"before": false, "after": true}],
        "space-infix-ops": "error",
        "spaced-comment": ["error", "always"],
        "operator-linebreak": ["error", "after"],
        "block-spacing": ["error", "never"],
        "key-spacing": ["error", {"mode": "minimum"}],
        "object-curly-spacing": ["error", "never"],
        "object-curly-newline": ["error", {"consistent": true}],

        "no-multiple-empty-lines": "error",

        // Actually, Atom already deals with this
        "no-trailing-spaces": "error",
        "eol-last": ["error", "always"],

        "no-console": [
          "warn",
          {"allow": ["warn", "error"]}
        ],
        "no-var": "warn",
        // "prefer-const": "warn",
        // "prefer-arrow-callback": ["error", {"allowNamedFunctions": true}],
        "prefer-template": "warn",
        "template-curly-spacing": "error",
        "no-useless-rename": "warn",
        "no-eval": "warn",

        "react/jsx-uses-react": "error",
        "react/jsx-uses-vars": "error"
    }
};
