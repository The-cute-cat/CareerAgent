module.exports = {
  rules: {
    // 最多允许2个空行
    'no-multiple-empty-lines': ['error', { max: 2, maxBOF: 0, maxEOF: 2 }],
    
    // 禁止连续多个空行
    'no-trailing-spaces': 'error',
    
    // 控制函数之间的空行
    'padding-line-between-statements': [
      'error',
      { blankLine: 'always', prev: '*', next: 'function' },
      { blankLine: 'always', prev: 'function', next: '*' }
    ]
  }
}
