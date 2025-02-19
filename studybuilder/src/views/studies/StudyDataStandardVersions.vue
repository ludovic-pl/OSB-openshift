<template>
  <div class="px-4">
    <div class="page-title d-flex align-center">
      {{ $t('StudyDataStandardVersionsView.title') }}
    </div>
    <v-tabs v-model="tab" bg-color="white">
      <v-tab v-for="item of tabs" :key="item.tab" :value="item.tab">
        {{ item.name }}
      </v-tab>
    </v-tabs>
    <v-window v-model="tab">
      <v-window-item value="controlled_terminology">
        <CTStandardVersionsTable
          :key="`controlled_terminology-${tabKeys.controlled_terminology}`"
        />
      </v-window-item>
      <v-window-item value="dictionaries">
        <UnderConstruction />
      </v-window-item>
      <v-window-item value="data_exchange">
        <UnderConstruction />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useTabKeys } from '@/composables/tabKeys'
import CTStandardVersionsTable from '@/components/studies/dataStandardVersions/CTStandardVersionsTable.vue'
import UnderConstruction from '@/components/layout/UnderConstruction.vue'

const { t } = useI18n()
const appStore = useAppStore()
const studiesGeneralStore = useStudiesGeneralStore()
const route = useRoute()
const router = useRouter()
const { tabKeys, updateTabKey } = useTabKeys()

const tab = ref(null)

const tabs = [
  {
    tab: 'controlled_terminology',
    name: t('StudyDataStandardVersionsView.tab1_title'),
  },
  { tab: 'dictionaries', name: t('StudyDataStandardVersionsView.tab2_title') },
  { tab: 'data_exchange', name: t('StudyDataStandardVersionsView.tab3_title') },
]

watch(tab, (newValue) => {
  const tabName = newValue
    ? tabs.find((el) => el.tab === newValue).name
    : tabs[0].name
  router.push({
    name: 'StudyDataStandardVersions',
    params: { study_id: studiesGeneralStore.selectedStudy.uid, tab: newValue },
  })
  appStore.addBreadcrumbsLevel(
    tabName,
    {
      name: 'StudyDataStandardVersions',
      params: { study_id: studiesGeneralStore.selectedStudy.uid, tab: tabName },
    },
    3,
    true
  )
  updateTabKey(newValue)
})

onMounted(() => {
  tab.value = route.params.tab || tabs[0].tab
})
</script>
