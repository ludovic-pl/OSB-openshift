import repository from './repository'

const resource = 'feature-flags'

export default {
  get(params) {
    return repository.get(`system/${resource}`, { params })
  },
  update(featureFlagId, payload) {
    return repository.patch(`${resource}/${featureFlagId}`, payload)
  },
}
