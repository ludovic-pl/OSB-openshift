<template>
  <div class="px-4">
    <div class="mb-6 d-flex align-center">
      <strong>{{ $t('_global.library') }}</strong>
      <span class="ml-2 text-secondary">{{ codelistNames.library_name }}</span>
      <v-spacer />
      <strong>{{ $t('CodeListDetail.concept_id') }}</strong>
      <span class="ml-2 text-secondary">{{ codelistNames.codelist_uid }}</span>
      <v-spacer />
      <v-btn
        size="small"
        :title="$t('CodelistTable.show_terms')"
        icon="mdi-dots-horizontal"
        @click="openCodelistTerms()"
      />
    </div>
    <div class="v-label pa-4">
      {{ $t('CodeListDetail.sponsor_title') }}
    </div>
    <v-table :aria-label="$t('CodeListDetail.sponsor_title')">
      <thead>
        <tr class="bg-greyBackground">
          <th width="25%">
            {{ $t('CodeListDetail.ct_identifiers') }}
          </th>
          <th width="50%">
            {{ $t('CodeListDetail.selected_values') }}
          </th>
          <th width="5%">
            {{ $t('_global.status') }}
          </th>
          <th width="10%">
            {{ $t('_global.modified') }}
          </th>
          <th width="5%">
            {{ $t('_global.version') }}
          </th>
          <th width="5%">
            {{ $t('_global.actions') }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{{ $t('CodeListDetail.sponsor_pref_name') }}</td>
          <td>{{ codelistNames.name }}</td>
          <td data-cy="names-status" rowspan="2">
            <StatusChip :status="codelistNames.status" />
          </td>
          <td rowspan="2">
            {{ $filters.date(codelistNames.start_date) }}
          </td>
          <td data-cy="names-version" rowspan="2">
            {{ codelistNames.version }}
          </td>
          <td rowspan="2">
            <v-btn
              v-if="
                codelistNames.possible_actions.find(
                  (action) => action === 'edit'
                )
              "
              data-cy="edit-sponsor-values"
              icon="mdi-pencil-outline"
              color="primary"
              :title="$t('CodeListDetail.edit_sponsor_values')"
              variant="text"
              @click="editSponsorValues"
            />
            <v-btn
              v-if="
                codelistNames.possible_actions.find(
                  (action) => action === 'approve'
                )
              "
              data-cy="approve-sponsor-values"
              color="success"
              icon="mdi-check-decagram"
              :title="$t('CodeListDetail.approve_sponsor_values_version')"
              variant="text"
              @click="approveSponsorValues"
            />
            <v-btn
              v-if="
                codelistNames.possible_actions.find(
                  (action) => action === 'new_version'
                )
              "
              data-cy="create-new-sponsor-values"
              color="primary"
              icon="mdi-plus-circle-outline"
              :title="$t('CodeListDetail.new_version')"
              variant="text"
              @click="createNewSponsorValuesVersion"
            />
            <v-btn
              data-cy="sponsor-values-version-history"
              icon="mdi-history"
              :title="$t('CodeListDetail.history')"
              variant="text"
              @click="openNamesHistory"
            />
          </td>
        </tr>
        <tr>
          <td>{{ $t('CodeListDetail.tpl_parameter') }}</td>
          <td>{{ $filters.yesno(codelistNames.template_parameter) }}</td>
        </tr>
      </tbody>
    </v-table>

    <div class="v-label pa-4 mt-6">
      {{ $t('CodeListDetail.attributes_title') }}
    </div>
    <v-table :aria-label="$t('CodeListDetail.attributes_title')">
      <thead>
        <tr class="bg-greyBackground">
          <th width="25%">
            {{ $t('CodeListDetail.ct_identifiers') }}
          </th>
          <th width="45%">
            {{ $t('CodeListDetail.selected_values') }}
          </th>
          <th width="5%">
            {{ $t('_global.status') }}
          </th>
          <th width="10%">
            {{ $t('_global.modified') }}
          </th>
          <th width="5%">
            {{ $t('_global.version') }}
          </th>
          <th width="10%">
            {{ $t('_global.actions') }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{{ $t('CodeListDetail.codelist_name') }}</td>
          <td>{{ attributes.name }}</td>
          <td data-cy="attributes-status" rowspan="5">
            <StatusChip :status="attributes.status" />
          </td>
          <td rowspan="5">
            {{ $filters.date(attributes.start_date) }}
          </td>
          <td data-cy="attributes-version" rowspan="5">
            {{ attributes.version }}
          </td>
          <td rowspan="5">
            <v-btn
              v-if="
                attributes.possible_actions.find((action) => action === 'edit')
              "
              icon="mdi-pencil-outline"
              color="primary"
              :title="$t('CodeListDetail.edit_sponsor_values')"
              variant="text"
              @click="editAttributes"
            />
            <v-btn
              v-if="
                attributes.possible_actions.find(
                  (action) => action === 'approve'
                )
              "
              data-cy="approve-attributes-values"
              color="success"
              icon="mdi-check-decagram"
              :title="$t('CodeListDetail.approve_attributes_version')"
              variant="text"
              @click="approveAttributes"
            />
            <v-btn
              v-if="
                attributes.possible_actions.find(
                  (action) => action === 'new_version'
                )
              "
              color="primary"
              icon="mdi-plus-circle-outline"
              :title="$t('CodeListDetail.new_attributes_version')"
              variant="text"
              @click="createNewAttributesVersion"
            />
            <v-btn
              icon="mdi-history"
              :title="$t('CodeListDetail.history')"
              variant="text"
              @click="openAttributesHistory"
            />
          </td>
        </tr>
        <tr>
          <td>{{ $t('CodeListDetail.submission_value') }}</td>
          <td>{{ attributes.submission_value }}</td>
        </tr>
        <tr>
          <td>{{ $t('CodeListDetail.nci_pref_name') }}</td>
          <td>{{ attributes.nci_preferred_name }}</td>
        </tr>
        <tr>
          <td>{{ $t('CodeListDetail.extensible') }}</td>
          <td>{{ $filters.yesno(attributes.extensible) }}</td>
        </tr>
        <tr>
          <td>{{ $t('CodeListDetail.definition') }}</td>
          <td>{{ attributes.definition }}</td>
        </tr>
      </tbody>
    </v-table>

    <v-dialog
      v-model="showSponsorValuesForm"
      persistent
      max-width="800px"
      @keydown.esc="showSponsorValuesForm = false"
    >
      <CodelistSponsorValuesForm
        v-model="codelistNames"
        @close="showSponsorValuesForm = false"
      />
    </v-dialog>
    <v-dialog
      v-model="showAttributesForm"
      persistent
      max-width="800px"
      @keydown.esc="showAttributesForm = false"
    >
      <CodelistAttributesForm
        v-model="attributes"
        @close="showAttributesForm = false"
      />
    </v-dialog>
    <v-dialog
      v-model="showHistory"
      persistent
      :fullscreen="$globals.historyDialogFullscreen"
      @keydown.esc="closeHistory"
    >
      <HistoryTable
        :title="historyTitle"
        :headers="historyHeaders"
        :items="historyItems"
        @close="closeHistory"
      />
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import controlledTerminology from '@/api/controlledTerminology'
import CodelistAttributesForm from '@/components/library/CodelistAttributesForm.vue'
import CodelistSponsorValuesForm from '@/components/library/CodelistSponsorValuesForm.vue'
import dataFormating from '@/utils/dataFormating'
import HistoryTable from '@/components/tools/HistoryTable.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import { useAppStore } from '@/stores/app'

const { t } = useI18n()
const eventBusEmit = inject('eventBusEmit')
const appStore = useAppStore()
const route = useRoute()
const router = useRouter()

const attributes = ref({ possible_actions: [] })
const codelistNames = ref({ possible_actions: [] })
const attributesHistoryHeaders = [
  { title: t('CodeListDetail.codelist_name'), key: 'name' },
  {
    title: t('CodeListDetail.submission_value'),
    key: 'submission_value',
  },
  {
    title: t('CodeListDetail.nci_pref_name'),
    key: 'nci_preferred_name',
  },
  { title: t('CodeListDetail.extensible'), key: 'extensible' },
  { title: t('_global.definition'), key: 'definition' },
  { title: t('_global.status'), key: 'status' },
  { title: t('_global.version'), key: 'version' },
]
const historyHeaders = ref([])
const historyItems = ref([])
const historyTitle = ref('')

const namesHistoryHeaders = [
  { title: t('CodeListDetail.sponsor_pref_name'), key: 'name' },
  {
    title: t('CodeListDetail.tpl_parameter'),
    key: 'template_parameter',
  },
  { title: t('_global.status'), key: 'status' },
  { title: t('_global.version'), key: 'version' },
]
const showAttributesForm = ref(false)
const showHistory = ref(false)
const showSponsorValuesForm = ref(false)

const namesHistoryTitle = computed(() => {
  return t('CodeListDetail.names_history_title', {
    codelist: codelistNames.value.codelist_uid,
  })
})
const attributesHistoryTitle = computed(() => {
  return t('CodeListDetail.attributes_history_title', {
    codelist: attributes.value.codelist_uid,
  })
})

onMounted(() => {
  controlledTerminology
    .getCodelistNames(route.params.codelist_id)
    .then((resp) => {
      codelistNames.value = resp.data
      appStore.addBreadcrumbsLevel(
        codelistNames.value.codelist_uid,
        { name: 'CodeListDetail', params: route.params },
        4
      )
    })
  controlledTerminology
    .getCodelistAttributes(route.params.codelist_id)
    .then((resp) => {
      attributes.value = resp.data
    })
})

function editSponsorValues() {
  showSponsorValuesForm.value = true
}
function editAttributes() {
  showAttributesForm.value = true
}
function createNewSponsorValuesVersion() {
  controlledTerminology
    .newCodelistNamesVersion(codelistNames.value.codelist_uid)
    .then((resp) => {
      codelistNames.value = resp.data
      eventBusEmit('notification', {
        msg: t('CodeListDetail.new_version_success'),
      })
    })
}
function approveSponsorValues() {
  controlledTerminology
    .approveCodelistNames(codelistNames.value.codelist_uid)
    .then((resp) => {
      codelistNames.value = resp.data
      eventBusEmit('notification', {
        msg: t('CodeListDetail.sponsor_values_approve_success'),
      })
    })
}
async function openNamesHistory() {
  historyTitle.value = namesHistoryTitle
  historyHeaders.value = namesHistoryHeaders
  const resp = await controlledTerminology.getCodelistNamesVersions(
    codelistNames.value.codelist_uid
  )
  historyItems.value = transformHistoryItems(resp.data)
  showHistory.value = true
}
function closeHistory() {
  showHistory.value = false
}
function createNewAttributesVersion() {
  controlledTerminology
    .newCodelistAttributesVersion(attributes.value.codelist_uid)
    .then((resp) => {
      attributes.value = resp.data
      eventBusEmit('notification', {
        msg: t('CodeListDetail.new_attributes_version_success'),
      })
    })
}
function approveAttributes() {
  controlledTerminology
    .approveCodelistAttributes(attributes.value.codelist_uid)
    .then((resp) => {
      attributes.value = resp.data
      eventBusEmit('notification', {
        msg: t('CodeListDetail.attributes_approve_success'),
      })
    })
}
async function openAttributesHistory() {
  historyTitle.value = attributesHistoryTitle
  historyHeaders.value = attributesHistoryHeaders
  const resp = await controlledTerminology.getCodelistAttributesVersions(
    attributes.value.codelist_uid
  )
  historyItems.value = transformHistoryItems(resp.data)
  showHistory.value = true
}
function openCodelistTerms() {
  router.push({
    name: 'CodelistTerms',
    params: { codelist_id: codelistNames.value.codelist_uid },
  })
}
function transformHistoryItems(items) {
  const result = []
  for (const item of items) {
    const newItem = { ...item }
    if (newItem.template_parameter !== undefined) {
      newItem.template_parameter = dataFormating.yesno(
        newItem.template_parameter
      )
    }
    if (newItem.extensible !== undefined) {
      newItem.extensible = dataFormating.yesno(newItem.extensible)
    }
    result.push(newItem)
  }
  return result
}
</script>
