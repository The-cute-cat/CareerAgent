export const VirtualHumanConfig = {
  APP_ID:'6f7f81e9',
  API_KEY:'126348302a25d01af053468a1f2115f6',
  API_SECRET:'ZDE4MGQ5ZjgxYzNhZjBiODNlMzliZmQ2',
  API_SECRET_ENCODING:'base64' as 'plain' | 'base64',
  SCENE_ID:'302073125141614592',
  SERVER_URL:'wss://avatar.cn-huadong-1.xf-yun.com/v1/interact',

  DEFAULT_AVATAR_ID: '138801001',
  DEFAULT_VCN:'x4_yezi',

  RENDER_WIDTH: 720,
  RENDER_HEIGHT: 1280,

  VOICES: [
    { label: '叶子', value: 'x4_yezi', gender: '女' },
    { label: '小燕', value: 'xiaoyan', gender: '女' },
    { label: '小峰', value: 'xiaofeng', gender: '男' }
  ] as const
}

export type VirtualHumanVoice = (typeof VirtualHumanConfig.VOICES)[number]['value']
