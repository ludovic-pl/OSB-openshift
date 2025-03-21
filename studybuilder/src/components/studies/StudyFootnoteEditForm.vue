<template>
  <StudySelectionEditForm
    v-if="editedObject"
    ref="form"
    :title="$t('StudyFootnoteEditForm.title')"
    :study-selection="editedObject"
    :template="template"
    :library-name="library.name"
    object-type="footnote"
    :open="open"
    :get-object-from-selection="(selection) => selection.footnote"
    :prepare-template-payload-func="prepareTemplatePayload"
    @init-form="initForm"
    @submit="submit"
    @close="close"
  >
    <template #formFields="{}">
      <p class="mt-6 text-secondary text-h6">
        {{ $t('StudyFootnoteEditForm.linked_items') }}
      </p>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-if="referencedSoAGroups.length > 0"
            v-model="referencedSoAGroups"
            :label="$t('StudyFootnoteEditForm.ref_soa_groups')"
            density="compact"
            disabled
            readonly
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-if="referencedActivities.length > 0"
            v-model="referencedActivities"
            :label="$t('StudyFootnoteEditForm.ref_activities')"
            density="compact"
            disabled
            readonly
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-if="referencedEpochsAndVisits.length > 0"
            v-model="referencedEpochsAndVisits"
            :label="$t('StudyFootnoteEditForm.ref_epochs_visits')"
            density="compact"
            disabled
            readonly
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-if="referencedSchedules.length > 0"
            v-model="referencedSchedules"
            :label="$t('StudyFootnoteEditForm.ref_schedules')"
            density="compact"
            disabled
            readonly
          />
        </v-col>
      </v-row>
    </template>
  </StudySelectionEditForm>
</template>

<script>
import { computed } from 'vue'
import constants from '@/constants/libraries'
import _isEmpty from 'lodash/isEmpty'
import formUtils from '@/utils/forms'
import study from '@/api/study'
import StudySelectionEditForm from './StudySelectionEditForm.vue'
import terms from '@/api/controlledTerminology/terms'
import footnoteConstants from '@/constants/footnotes'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useFootnotesStore } from '@/stores/studies-footnotes'

export default {
  components: {
    StudySelectionEditForm,
  },
  inject: ['eventBusEmit'],
  props: {
    studyFootnote: {
      type: Object,
      default: undefined,
    },
    open: Boolean,
  },
  emits: ['close', 'enableFootnoteMode', 'updated'],
  setup() {
    const studiesGeneralStore = useStudiesGeneralStore()
    const footnotesStore = useFootnotesStore()
    return {
      selectedStudy: computed(() => studiesGeneralStore.selectedStudy),
      footnotesStore,
    }
  },
  data() {
    return {
      editedObject: {},
      referencedSoAGroups: [],
      referencedActivities: [],
      referencedEpochsAndVisits: [],
      referencedSchedules: [],
    }
  },
  computed: {
    template() {
      return this.editedObject.footnote
        ? this.editedObject.footnote.template
        : this.editedObject.template
    },
    library() {
      return this.studyFootnote.footnote
        ? this.studyFootnote.footnote.library
        : this.studyFootnote.template.library
    },
  },
  watch: {
    studyFootnote: {
      handler: function (value) {
        if (!_isEmpty(value)) {
          study
            .getStudyFootnote(this.selectedStudy.uid, this.studyFootnote.uid)
            .then((resp) => {
              this.editedObject = resp.data
            })
        }
      },
      immediate: true,
    },
  },
  mounted() {
    terms.getByCodelist('footnoteTypes').then((resp) => {
      for (const type of resp.data.items) {
        if (
          type.name.sponsor_preferred_name ===
          footnoteConstants.FOOTNOTE_TYPE_SOA
        ) {
          this.footnoteType = type
          break
        }
      }
    })
  },
  methods: {
    initForm(form) {
      this.originalForm = JSON.parse(JSON.stringify(form))
      this.referencedActivities = []
      this.referencedEpochsAndVisits = []
      this.studyFootnote.referenced_items.forEach((item) => {
        if (['StudySoAGroup'].indexOf(item.item_type) > -1) {
          this.referencedSoAGroups.push(item.item_name)
        } else if (
          [
            'StudyActivity',
            'StudyActivityGroup',
            'StudyActivitySubGroup',
          ].indexOf(item.item_type) > -1
        ) {
          this.referencedActivities.push(item.item_name)
        } else if (['StudyVisit', 'StudyEpoch'].indexOf(item.item_type) > -1) {
          this.referencedEpochsAndVisits.push(item.item_name)
        } else if (['StudyActivitySchedule'].indexOf(item.item_type) > -1) {
          this.referencedSchedules.push(item.item_name)
        }
      })
      this.referencedActivities = this.removeDuplicates(
        this.referencedActivities
      ).join(', ')
      this.referencedSoAGroups = this.removeDuplicates(
        this.referencedSoAGroups
      ).join(', ')
      this.referencedEpochsAndVisits = this.referencedEpochsAndVisits.join(', ')
      this.referencedSchedules = this.referencedSchedules.join(', ')
    },
    removeDuplicates(arr) {
      return arr.filter((item, index, self) => {
        return self.indexOf(item) === index
      })
    },
    prepareTemplatePayload(data) {
      data.type_uid = this.footnoteType.term_uid
    },
    async submit(newTemplate, form, parameters) {
      const payload = formUtils.getDifferences(this.originalForm, form)
      payload.parameters = parameters
      if (_isEmpty(payload) && !newTemplate) {
        this.eventBusEmit('notification', {
          msg: this.$t('_global.no_changes'),
          type: 'info',
        })
        this.$refs.form.close()
        return
      }
      const args = {
        studyUid: this.selectedStudy.uid,
        studyFootnoteUid: this.editedObject.uid,
        form: payload,
        library: {
          name: constants.LIBRARY_USER_DEFINED,
        },
      }
      if (newTemplate) {
        args.template = newTemplate
      } else {
        args.template = this.template
      }
      await this.footnotesStore.updateStudyFootnote(args)
      this.eventBusEmit('notification', {
        msg: this.$t('StudyFootnoteEditForm.update_success'),
      })
      this.$emit('updated')
      this.$refs.form.close()
    },
    close() {
      this.referencedSoAGroups = []
      this.referencedActivities = []
      this.referencedEpochsAndVisits = []
      this.referencedSchedules = []
      this.$emit('close')
    },
  },
}
</script>
