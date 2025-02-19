import { inject } from 'vue'

function extractStudyUidFromUrl(path) {
  const studyUidMatch = path.match(/\/studies\/(Study_[0-9]+)/i)
  if (studyUidMatch) {
    return studyUidMatch[1]
  } else {
    return null
  }
}

function extractStudyUidFromLocalStorage() {
  const selectedStudy = JSON.parse(localStorage.getItem('selectedStudy'))
  if (selectedStudy) {
    return selectedStudy.uid
  } else {
    return null
  }
}

export function getAppEnv() {
  const $config = inject('$config')
  const { APP_ENV } = $config

  if (!APP_ENV) return ''

  let appEnv = APP_ENV.toUpperCase()

  if (appEnv.startsWith('PRD')) return ''

  const env = appEnv.startsWith('EDU') ? appEnv : appEnv.split(' ', 2)[0]

  return env
}

export default {
  extractStudyUidFromUrl,
  extractStudyUidFromLocalStorage,
}
