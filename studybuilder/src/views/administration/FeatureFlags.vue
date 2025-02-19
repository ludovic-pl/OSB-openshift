<template>
  <div class="px-4">
    <div class="page-title d-flex align-center">
      {{ $t('FeatureFlagsView.title') }}
    </div>
    <v-card>
      <v-card-text>
        <v-alert
          color="nnLightBlue200"
          icon="mdi-information-outline"
          class="text-nnTrueBlue mx-4 my-2"
        >
          {{ $t('FeatureFlagsView.help') }}
        </v-alert>

        <v-data-table :headers="headers" :items="flags" class="mx-4 my-6">
          <template #[`item.actions`]="{ item }">
            <v-switch
              v-model="item.enabled"
              color="primary"
              hide-details
              @update:model-value="(value) => toggleFlagState(item, value)"
            />
          </template>
          <template #bottom></template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import featureFlagsApi from '@/api/featureFlags'

const { t } = useI18n()

const flags = ref([])

const headers = [
  { key: 'actions', title: '', width: '6%' },
  { key: 'name', title: t('_global.name'), width: '45%' },
  { key: 'description', title: t('_global.description'), width: '45%' },
]

async function toggleFlagState(flag, value) {
  await featureFlagsApi.update(flag.sn, { enabled: value })
}

featureFlagsApi.get().then((resp) => {
  flags.value = resp.data
})
</script>

<style scoped>
.v-data-table {
  width: auto !important;
}
</style>
