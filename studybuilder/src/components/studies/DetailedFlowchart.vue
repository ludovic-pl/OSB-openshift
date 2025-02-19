<template>
  <div
    v-if="!loadingSoaContent"
    v-resize="onResize"
    class="pa-4 bg-white"
    style="overflow-x: auto"
  > 
    <v-row style="justify-content: center">
      <v-btn-toggle
        v-model="layout"
        mandatory
        density="compact"
        color="nnBaseBlue"
        divided
        variant="outlined"
        class="layoutSelector"
      >
        <v-btn value="detailed">
          {{ $t('DetailedFlowchart.detailed') }}
        </v-btn>
        <v-btn value="protocol">
          {{ $t('DetailedFlowchart.protocol') }}
        </v-btn>
        <v-btn value="operational">
          {{ $t('DetailedFlowchart.operational') }}
        </v-btn>
      </v-btn-toggle>
    </v-row>
    <ProtocolFlowchart
      v-if="['operational', 'protocol'].indexOf(layout) > -1"
      :layout="layout"
      :style="`max-height: ${tableHeight + 70}px;`"
    />
    <div v-else>
      <div class="d-flex align-center mb-4">
        <v-switch
          v-model="expandAllRows"
          :label="$t('DetailedFlowchart.expand_all')"
          hide-details
          class="ml-2 flex-grow-0"
          color="primary"
          @update:model-value="toggleAllRowState"
        />
        <v-spacer />
        <template v-if="!readOnly">
          <v-btn
            v-show="multipleConsecutiveVisitsSelected()"
            class="ml-2"
            size="small"
            variant="outlined"
            color="nnBaseBlue"
            :title="$t('GroupStudyVisits.title')"
            :disabled="
            footnoteMode ||
            !checkPermission($roles.STUDY_WRITE) ||
            selectedStudyVersion !== null
            "
            :loading="soaContentLoadingStore.loading"
            icon="mdi-arrow-expand-horizontal"
            @click="groupSelectedVisits()"
          />
          <v-btn
            class="ml-2"
            size="small"
            variant="outlined"
            color="nnBaseBlue"
            :title="$t('DetailedFlowchart.hide_activity_selection')"
            :disabled="
            footnoteMode ||
            !checkPermission($roles.STUDY_WRITE) ||
            selectedStudyVersion !== null
            "
            icon="mdi-eye-off-outline"
            :loading="soaContentLoadingStore.loading"
            @click="toggleActivitySelectionDisplay(false)"
          />
          <v-btn
            class="ml-2"
            size="small"
            variant="outlined"
            color="nnBaseBlue"
            :title="$t('DetailedFlowchart.show_activity_selection')"
            :disabled="
            footnoteMode ||
            !checkPermission($roles.STUDY_WRITE) ||
            selectedStudyVersion !== null
            "
            icon="mdi-eye-outline"
            :loading="soaContentLoadingStore.loading"
            @click="toggleActivitySelectionDisplay(true)"
          />
          <v-menu 
            :disabled="
            footnoteMode ||
            !checkPermission($roles.STUDY_WRITE) ||
            selectedStudyVersion !== null
            "
            rounded
            location="bottom">
            <template #activator="{ props }">
              <v-btn
                :disabled="
                footnoteMode ||
                !checkPermission($roles.STUDY_WRITE) ||
                selectedStudyVersion !== null
                "
                class="ml-2"
                size="small"
                variant="outlined"
                color="nnBaseBlue"
                v-bind="props"
                title="Bulk actions"
                icon="mdi-folder-multiple-outline"
                :loading="soaContentLoadingStore.loading"
              >
              </v-btn>
            </template>

            <v-list density="compact" rounded="xl">
              <v-list-item prepend-icon="mdi-pencil-outline" @click="openBatchEditForm">
                <v-list-item-title>{{ $t('DetailedFlowchart.bulk_edit') }}</v-list-item-title>
              </v-list-item>
              <v-list-item prepend-icon="mdi-delete-outline" link @click="batchRemoveStudyActivities">
                <v-list-item-title>{{ $t('DetailedFlowchart.bulk_remove') }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
          <v-menu rounded location="bottom">
            <template #activator="{ props }">
              <v-btn
                class="ml-2"
                size="small"
                variant="outlined"
                color="nnBaseBlue"
                v-bind="props"
                :title="$t('DataTableExportButton.export')"
                icon="mdi-download-outline"
                :loading="soaContentLoadingStore.loading"
              />
            </template>
            <v-list>
              <v-list-item link @click="downloadCSV">
                <v-list-item-title>CSV</v-list-item-title>
              </v-list-item>
              <v-list-item link @click="downloadEXCEL">
                <v-list-item-title>EXCEL</v-list-item-title>
              </v-list-item>
              <v-list-item link @click="downloadDOCX">
                <v-list-item-title>DOCX</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
          <v-btn
            class="ml-2"
            size="small"
            variant="outlined"
            color="nnBaseBlue"
            :title="$t('NNTableTooltips.history')"
            icon="mdi-history"
            @click="openHistory"
          />
        </template>
      </div>
      <div
        ref="tableContainer"
        class="sticky-header"
        :style="`max-height: ${tableHeight}px; min-height: 500px; border-radius: 15px;`"
      >
        <table :aria-label="$t('DetailedFlowchart.table_caption')">
          <thead>
            <tr ref="firstHeader">
              <th
                ref="firstCol"
                scope="col"
                class="header zindex25 pl-6 pt-3"
                style="left: 0px"
              >
                {{ $t('DetailedFlowchart.study_epoch') }}
              </th>
              <th
                ref="secondCol"
                :rowspan="numHeaderRows"
                scope="col"
                class="header zindex25"
                :style="`left: ${firstColWidth}px !important;`"
              />
              <th
                :rowspan="numHeaderRows"
                scope="col"
                class="header zindex25"
                :style="`left: ${firstColWidth + secondColWidth}px !important;`"
              />
              <template v-if="soaContent">
                <th
                  v-for="(cell, index) in soaEpochRow"
                  :key="`epoch-${index}`"
                  class="header"
                  scope="col"
                >
                  <v-row>
                    <v-badge
                      color="transparent"
                      text-color="nnWhite"
                      floating
                      :content="
                      cell.refs ? getElementFootnotesLetters(cell.refs[0].uid) : ''
                      "
                      class="mt-3 mr-1 ml-2 mb-2"
                    >
                      {{ cell.text }}
                    </v-badge>
                    <v-btn
                      v-if="
                            footnoteMode &&
                            cell.text !== '' &&
                            !checkIfElementHasFootnote(cell.refs[0].uid)
                            "
                      size="small"
                      icon="mdi-plus-circle-outline"
                      class="mt-1 mx-0 px-0"
                      color="nnWhite"
                      variant="text"
                      @click="
                      addElementForFootnote(
                        cell.refs[0].uid,
                        'StudyEpoch',
                        cell.text
                      )
                      " />
                    <v-btn
                      v-else-if="
                                 footnoteMode &&
                                 cell.text !== '' &&
                                 checkIfElementHasFootnote(cell.refs[0].uid)
                                 "
                      size="small"
                      icon="mdi-minus-circle"
                      color="nnWhite"
                      class="mt-1 mx-0 px-0"
                      variant="text"
                      @click="removeElementForFootnote(cell.refs[0].uid)"
                    /></v-row>
                </th>
              </template>
              <template v-else>
                <th colspan="2" scope="col" />
              </template>
            </tr>
            <tr v-if="soaMilestoneRow.length" ref="milestoneHeader">
              <th
                width="10%"
                scope="col"
                :style="`top: ${firstHeaderHeight}px;`"
                class="header zindex25 pl-6"
              >
                {{ $t('DetailedFlowchart.study_milestone') }}
              </th>
              <th
                v-for="(cell, index) in soaMilestoneRow"
                :key="`milestone-${index}`"
                class="header"
                scope="col"
                :style="`top: ${firstHeaderHeight}px`"
              >
                {{ cell.text }}
              </th>
            </tr>
            <tr ref="secondHeader">
              <th
                :style="`top: ${firstHeaderHeight + milestoneHeaderHeight}px; align-content: center;`"
                scope="col"
                class="header zindex25 pl-6"
              >
                {{ $t('DetailedFlowchart.visit_short_name') }}
              </th>
              <template v-if="soaContent">
                <th
                  v-for="(cell, index) in soaVisitRow"
                  :key="`shortName-${index}`"
                  :style="`top: ${firstHeaderHeight + milestoneHeaderHeight}px`"
                  scope="col"
                >
                  <div class="d-flex align-center">
                    <v-badge
                      color="transparent"
                      text-color="secondary"
                      floating
                      :content="
                      cell.refs.length
                      ? getElementFootnotesLetters(cell.refs[0].uid)
                      : ''
                      "
                      class="visitFootnote"
                    >
                      {{ cell.text }}
                    </v-badge>
                    <v-btn
                      v-if="
                            footnoteMode &&
                            !checkIfElementHasFootnote(cell.refs[0].uid)
                            "
                      size="small"
                      icon="mdi-plus-circle-outline"
                      class="mb-1 mx-0 px-0"
                      variant="text"
                      @click="
                      addElementForFootnote(
                        cell.refs[0].uid,
                        'StudyVisit',
                        cell.text
                      )
                      "
                    />
                    <v-btn
                      v-else-if="
                                 footnoteMode &&
                                 checkIfElementHasFootnote(cell.refs[0].uid)
                                 "
                      size="small"
                      icon="mdi-minus-circle"
                      color="nnBaseBlue"
                      class="mb-1 mx-0 px-0"
                      variant="text"
                      @click="removeElementForFootnote(cell.refs[0].uid)"
                    />
                    <v-checkbox
                      v-if="cell.refs.length === 1 && !footnoteMode"
                      v-model="selectedVisitIndexes"
                      :value="index"
                      hide-details
                      multiple
                      :disabled="
                      footnoteMode ||
                      !checkPermission($roles.STUDY_WRITE) ||
                      selectedStudyVersion !== null
                      "
                    />
                    <v-btn
                      v-else-if="!footnoteMode"
                      icon="mdi-delete-outline"
                      color="error"
                      size="x-small"
                      :title="$t('GroupStudyVisits.delete_title')"
                      :disabled="
                      footnoteMode ||
                      !checkPermission($roles.STUDY_WRITE) ||
                      selectedStudyVersion !== null
                      "
                      variant="text"
                      @click="deleteVisitGroup(cell.text)"
                    />
                  </div>
                </th>
              </template>
              <template v-else>
                <th
                  colspan="2"
                  :style="`top: ${firstHeaderHeight}px`"
                  scope="col"
                />
              </template>
            </tr>
            <tr ref="thirdHeader">
              <template v-if="soaContent">
                <th
                  v-for="(cell, index) in soaDayRow"
                  :key="`week-${index}`"
                  :style="`top: ${thirdHeaderRowTop}px`"
                  scope="col"
                  :class="
                  cell.text.includes('Study') ? 'header zindex25 pl-6' : ''
                  "
                >
                  {{ cell.text }}
                </th>
              </template>
              <template v-else>
                <th
                  colspan="2"
                  :style="`top: ${thirdHeaderRowTop}px`"
                  scope="col"
                />
              </template>
            </tr>
            <tr>
              <template v-if="soaContent">
                <th
                  v-for="(cell, index) in soaWindowRow"
                  :key="`window-${index}`"
                  :style="`top: ${fourthHeaderRowTop}px`"
                  scope="col"
                  :class="
                  cell.text.includes('Visit window') ? 'header zindex25 pl-6' : ''
                  "
                >
                  {{ cell.text }}
                </th>
              </template>
              <template v-else>
                <th
                  colspan="2"
                  :style="`top: ${fourthHeaderRowTop}px`"
                  scope="col"
                >
                </th>
              </template>
            </tr>
          </thead>
          <tbody>
            <template v-for="(row, index) in soaRows">
              <tr
                v-if="showSoaRow(index, row)"
                :key="`row-${index}`"
                :class="getSoaRowClasses(row)"
              >
                <td class="sticky-column" style="left: 0px">
                  <ActionsMenu
                    v-if="getSoaRowType(row) === 'activity'"
                    :actions="actions"
                    :item="row.cells[0].refs[0]"
                  />
                  <v-btn
                    v-if="!readOnly && getSoaRowType(row) !== 'activity'"
                    :icon="getDisplayButtonIcon(`row-${index}`)"
                    variant="text"
                    @click="toggleRowState(`row-${index}`)"
                  />
                </td>
                <td
                  :class="getSoaFirstCellClasses(row.cells[0])"
                  :style="`left: ${firstColWidth}px; min-width: 300px`"
                >
                  <div class="d-flex align-center justify-start">
                    <v-checkbox
                      v-if="
                            !readOnly &&
                            !footnoteMode &&
                            getSoaRowType(row) === 'activity'
                            "
                      color="primary"
                      hide-details
                      :model-value="
                      studyActivitySelection.findIndex(
                        (cell) =>
                        cell.refs[0].uid === row.cells[0].refs[0].uid
                      ) !== -1
                      "
                      :disabled="
                      !checkPermission($roles.STUDY_WRITE) ||
                      selectedStudyVersion !== null
                      "
                      class="flex-grow-0"
                      @update:model-value="
                             (value) => toggleActivitySelection(row, value)
                             "
                    />
                    <v-checkbox
                      v-if="
                            !readOnly &&
                            !footnoteMode &&
                            getSoaRowType(row) === 'subGroup'
                            "
                      color="primary"
                      true-icon="mdi-checkbox-multiple-marked-outline"
                      false-icon="mdi-checkbox-multiple-blank-outline"
                      hide-details
                      :disabled="
                      !checkPermission($roles.STUDY_WRITE) ||
                      selectedStudyVersion !== null
                      "
                      class="flex-grow-0 mr-2"
                      @update:model-value="
                             (value) => toggleSubgroupActivitiesSelection(row, value)
                             "
                    />
                    <v-badge
                      color="transparent"
                      text-color="secondary"
                      floating
                      :content="
                      row.cells[0].refs.length
                      ? getElementFootnotesLetters(row.cells[0].refs[0].uid)
                      : ''
                      "
                    >
                      <v-tooltip bottom>
                        <template #activator="{ props }">
                          <div v-bind="props">
                            <span class="text-uppercase">
                              {{ row.cells[0].text.substring(0, 40) }}
                            </span>
                          </div>
                        </template>
                        <span class="text-uppercase">
                          {{ row.cells[0].text }}
                        </span>
                      </v-tooltip>
                    </v-badge>
                    <v-btn
                      v-if="
                            footnoteMode &&
                            row.cells[0].refs[0] &&
                            !checkIfElementHasFootnote(row.cells[0].refs[0].uid)
                            "
                      icon="mdi-plus-circle-outline"
                      class="mx-0 px-0"
                      variant="text"
                      @click="
                      addElementForFootnote(
                        row.cells[0].refs[0].uid,
                        row.cells[0].refs[0].type,
                        row.cells[0].text
                      )
                      "
                    />
                    <v-btn
                      v-else-if="
                                 footnoteMode &&
                                 row.cells[0].refs[0] &&
                                 checkIfElementHasFootnote(row.cells[0].refs[0].uid)
                                 "
                      icon="mdi-minus-circle"
                      class="mx-0 px-0"
                      color="nnBaseBlue"
                      variant="text"
                      @click="
                      removeElementForFootnote(row.cells[0].refs[0].uid)
                      "
                    />
                  </div>
                </td>
                <td class="sticky-column" style="left: 400px !important">
                  <v-btn
                    v-if="!readOnly"
                    icon
                    :title="$t('DetailedFlowchart.toggle_soa_group_display')"
                    :disabled="
                    footnoteMode ||
                    !checkPermission($roles.STUDY_WRITE) ||
                    selectedStudyVersion !== null
                    "
                    variant="text"
                    @click="toggleLevelDisplay(row)"
                  >
                    <v-icon v-if="getLevelDisplayState(row)" color="success">
                      mdi-eye-outline
                    </v-icon>
                    <v-icon v-else> mdi-eye-off-outline </v-icon>
                  </v-btn>
                </td>
                <td
                  v-if="getSoaRowType(row) !== 'activity'"
                  :colspan="row.cells.length - 1"
                />
                <td
                  v-for="(visitCell, visitIndex) in soaVisitRow"
                  v-else
                  :key="`row-${index}-cell-${visitIndex}`"
                >
                  <v-row class="mt-0">
                    <v-badge
                      color="transparent"
                      text-color="secondary"
                      offset-y="18"
                      :content="
                      row.cells[visitIndex + 1].refs &&
                      row.cells[visitIndex + 1].refs.length
                      ? getElementFootnotesLetters(
                        row.cells[visitIndex + 1].refs[0].uid
                      )
                      : ''
                      "
                      overlap
                    >
                      <v-speed-dial
                        v-if="
                              !footnoteMode &&
                              !readOnly &&
                              currentSelectionMatrix[row.cells[0].refs[0].uid][
                              visitCell.refs[0].uid
                              ]
                              "
                        open-on-hover
                        submenu
                        location="right bottom"
                        transition="scale-transition"
                      >
                        <template #activator="{ props: activatorProps }">
                          <v-checkbox
                            v-bind="activatorProps"
                            v-model="
                                    currentSelectionMatrix[row.cells[0].refs[0].uid][
                                    visitCell.refs[0].uid
                                    ].value
                                    "
                            color="success"
                            :disabled="
                            isCheckboxDisabled(
                              row.cells[0].refs[0].uid,
                              visitCell.refs[0].uid
                            ) ||
                            footnoteMode ||
                            !checkPermission($roles.STUDY_WRITE) ||
                            selectedStudyVersion !== null
                            "
                            hide-details
                            true-icon="mdi-checkbox-marked-circle-outline"
                            false-icon="mdi-checkbox-blank-circle-outline"
                            class="mx-0 ml-2 px-0"
                            @update:model-value="
                                   (value) =>
                                   updateSchedule(
                                     value,
                                     row.cells[0].refs[0].uid,
                                     visitCell
                                   )
                                   "
                          />
                        </template>
                        <v-btn
                          key="1"
                          style="scale: 80%;"
                          size="x-small"
                          class="ml-n2 mb-1"
                          variant="outlined"
                          color="nnBaseBlue"
                          icon="mdi-plus"
                          @click="enableFootnoteModeWithElement(
                            row.cells[visitIndex + 1].refs[0].uid,
                            row.cells[visitIndex + 1].refs[0].type,
                            row.cells[visitIndex + 1].refs[0].text
                          )"
                        />
                        <v-btn
                          v-if="Boolean(getElementFootnotesLetters(
                                row.cells[visitIndex + 1].refs[0].uid
                                ))"
                          key="2"
                          class="ml-n2 mb-n3"
                          style="scale: 80%;"
                          size="x-small"
                          variant="outlined"
                          color="nnBaseBlue"
                          icon="mdi-minus"
                          @click="openRemoveFootnoteForm(row.cells[visitIndex + 1])"
                        />
                      </v-speed-dial>
                      <v-btn
                        v-else-if="
                                   footnoteMode &&
                                   currentSelectionMatrix[row.cells[0].refs[0].uid][
                                   visitCell.refs[0].uid
                                   ].uid &&
                                   !checkIfElementHasFootnote(
                                   row.cells[visitIndex + 1].refs[0].uid
                                   )
                                   "
                        icon="mdi-plus-circle-outline"
                        class="mx-0 px-0"
                        variant="text"
                        @click="
                        addElementForFootnote(
                          row.cells[visitIndex + 1].refs[0].uid,
                          row.cells[visitIndex + 1].refs[0].type,
                          row.cells[visitIndex + 1].refs[0].text
                        )
                        "
                      />
                      <v-btn
                        v-else-if="
                                   footnoteMode &&
                                   currentSelectionMatrix[row.cells[0].refs[0].uid][
                                   visitCell.refs[0].uid
                                   ].uid &&
                                   checkIfElementHasFootnote(
                                   row.cells[visitIndex + 1].refs[0].uid
                                   )
                                   "
                        icon="mdi-minus-circle"
                        class="mx-0 px-0"
                        color="nnBaseBlue"
                        variant="text"
                        @click="
                        removeElementForFootnote(
                          row.cells[visitIndex + 1].refs[0].uid
                        )
                        "
                      />
                    </v-badge>
                  </v-row>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
      <div class="mt-8 ml-n4 mr-n4">
        <StudyFootnoteTable
          @update="loadSoaContent()"
          @enable-footnote-mode="enableFootnoteMode"
          @remove-element-from-footnote="removeElementForFootnote"
        />
      </div>
    </div>
    <v-card v-if="footnoteMode" id="bottomCard" elevation="24" class="bottomCard">
      <v-row>
        <v-col cols="8">
          <v-card
            color="nnLightBlue200"
            class="ml-4"
            style="width: fit-content"
          >
            <v-card-text>
              <v-icon class="pb-1 mr-2">mdi-information-outline</v-icon>
              <div
                v-if="activeFootnote"
                v-html="
                      $t('StudyFootnoteEditForm.select_footnote_items', {
                      footnote: activeFootnote.template
                      ? activeFootnote.template.name_plain
                      : activeFootnote.footnote.name_plain,
                      })
                      "
              />
              <div v-else>
                {{
                $t('StudyFootnoteEditForm.select_to_create_footnote_items')
                }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" style="align-content: center; text-align-last: end">
          <v-btn
            color="nnBaseBlue"
            variant="outlined"
            size="large"
            rounded
            :text="$t('_global.cancel')"
            @click="disableFootnoteMode"
          />
          <v-btn
            color="nnBaseBlue"
            class="ml-2 mr-4"
            size="large"
            rounded
            :loading="footnoteUpdateLoading"
            :text="
            activeFootnote
            ? $t('StudyFootnoteEditForm.save_linking')
            : $t('_global.continue')
            "
            @click="saveElementsForFootnote"
          />
        </v-col>
      </v-row>
    </v-card>
    <v-dialog v-model="showActivityEditForm" max-width="600px">
      <StudyActivityEditForm
        :study-activity="selectedStudyActivity"
        @close="closeEditForm"
        @updated="loadSoaContent(true)"
      />
    </v-dialog>
    <v-dialog v-model="showDraftedActivityEditForm" max-width="600px">
      <StudyDraftedActivityEditForm
        :study-activity="selectedStudyActivity"
        @close="closeEditForm"
        @updated="loadSoaContent(true)"
      />
    </v-dialog>
    <RemoveFootnoteForm
      :open="showRemoveFootnoteForm"
      :item-uid="removeItemUid"
      @close="closeRemoveFootnoteForm"
    />
    <StudyActivityScheduleBatchEditForm
      :open="showBatchEditForm"
      :selection="formattedStudyActivitySelection"
      :current-selection-matrix="currentSelectionMatrix"
      @updated="() => loadSoaContent(true)"
      @close="showBatchEditForm = false"
      @remove="unselectItem"
    />
    <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
    <v-dialog v-model="showCollapsibleGroupForm" persistent max-width="1000px">
      <CollapsibleVisitGroupForm
        :open="showCollapsibleGroupForm"
        :visits="selectedVisits"
        @close="closeCollapsibleVisitGroupForm"
        @created="collapsibleVisitGroupCreated"
      />
    </v-dialog>
    <v-dialog
      v-model="showFootnoteForm"
      persistent
      fullscreen
      content-class="fullscreen-dialog"
    >
      <StudyFootnoteForm
        :current-study-footnotes="footnotesStore.studyFootnotes"
        :selected-elements="elementsForFootnote"
        class="fullscreen-dialog"
        @close="closeFootnoteForm"
        @added="table.filterTable()"
      />
    </v-dialog>
    <v-dialog
      v-model="showHistory"
      :fullscreen="$globals.historyDialogFullscreen"
      persistent
      @keydown.esc="closeHistory"
    >
      <HistoryTable
        :headers="historyHeaders"
        :items="historyItems"
        :items-total="historyItemsTotal"
        :title="historyTitle"
        change-field="action"
        @close="closeHistory"
        @refresh="(options) => getHistoryData(options)"
      />
    </v-dialog>
    <v-dialog
      v-model="showActivityForm"
      persistent
      fullscreen
      content-class="fullscreen-dialog"
    >
      <StudyActivityForm
        :exchange-mode="activityExchangeMode"
        :exchange-activity-uid="selectedStudyActivity"
        :order="flowchartActivityOrder"
        @close="closeActivityForm"
        @added="onActivityExchanged"
      />
    </v-dialog>
  </div>
  <v-skeleton-loader
    v-else
    class="mt-6 mx-auto"
    max-width="800px"
    type="table-heading, table-thead, table-tbody"
  />
</template>

<script>
import { computed } from 'vue'
import CollapsibleVisitGroupForm from './CollapsibleVisitGroupForm.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import HistoryTable from '@/components/tools/HistoryTable.vue'
import study from '@/api/study'
import StudyActivityScheduleBatchEditForm from './StudyActivityScheduleBatchEditForm.vue'
import StudyFootnoteTable from './StudyFootnoteTable.vue'
import studyEpochs from '@/api/studyEpochs'
import StudyFootnoteForm from '@/components/studies/StudyFootnoteForm.vue'
import dataFormating from '@/utils/dataFormating'
import _isEmpty from 'lodash/isEmpty'
import { useAccessGuard } from '@/composables/accessGuard'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useFootnotesStore } from '@/stores/studies-footnotes'
import { useSoaContentLoadingStore } from '@/stores/soa-content-loading'
import soaDownloads from '@/utils/soaDownloads'
import ProtocolFlowchart from './ProtocolFlowchart.vue'
import RemoveFootnoteForm from './RemoveFootnoteForm.vue'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import StudyActivityEditForm from './StudyActivityEditForm.vue'
import StudyDraftedActivityEditForm from './StudyDraftedActivityEditForm.vue'
import StudyActivityForm from './StudyActivityForm.vue'
import libraries from '@/constants/libraries.js'

export default {
  components: {
    CollapsibleVisitGroupForm,
    ConfirmDialog,
    HistoryTable,
    StudyActivityScheduleBatchEditForm,
    StudyFootnoteTable,
    ProtocolFlowchart,
    StudyFootnoteForm,
    RemoveFootnoteForm,
    ActionsMenu,
    StudyActivityEditForm,
    StudyDraftedActivityEditForm,
    StudyActivityForm
  },
  inject: ['eventBusEmit'],
  props: {
    readOnly: {
      type: Boolean,
      default: false,
    },
    update: {
      type: Number,
      default: 0,
    },
    redirectFootnote: {
      type: Object,
      default: undefined,
    },
  },
  setup() {
    const accessGuard = useAccessGuard()
    const studiesGeneralStore = useStudiesGeneralStore()
    const footnotesStore = useFootnotesStore()
    const soaContentLoadingStore = useSoaContentLoadingStore()
    return {
      selectedStudy: computed(() => studiesGeneralStore.selectedStudy),
      selectedStudyVersion: computed(
        () => studiesGeneralStore.selectedStudyVersion
      ),
      footnotesStore,
      ...accessGuard,
      soaContentLoadingStore,
    }
  },
  data() {
    return {
      currentSelectionMatrix: {},
      expandAllRows: false,
      rowsDisplayState: {},
      firstHeaderHeight: 0,
      secondHeaderHeight: 0,
      thirdHeaderHeight: 0,
      firstColWidth: 0,
      secondColWidth: 0,
      milestoneHeaderHeight: 0,
      selectedVisitIndexes: [],
      showBatchEditForm: false,
      showCollapsibleGroupForm: false,
      showFootnoteForm: false,
      studyActivities: [],
      studyActivitySchedules: [],
      studyActivitySelection: [],
      studyVisits: [],
      tableHeight: 700,
      activeFootnote: null,
      footnoteMode: false,
      elementsForFootnote: {
        referenced_items: [],
      },
      loadingSoaContent: false,
      selectedFootnote: null,
      showHistory: false,
      footnoteUpdateLoading: false,
      soaGroupsUpdate: false,
      historyHeaders: [
        {
          title: this.$t('DetailedFlowchart.history_object_type'),
          key: 'object_type',
        },
        { title: this.$t('_global.description'), key: 'description' },
        { title: this.$t('_global.modified_by'), key: 'author_username' },
      ],
      historyItems: [],
      historyItemsTotal: 0,
      soaContent: null,
      layout: 'detailed',
      showRemoveFootnoteForm: false,
      removeItemUid: '',
      actions: [
        {
          label: this.$t('DetailedFlowchart.edit_activity'),
          icon: 'mdi-pencil-outline',
          condition: () => !this.selectedStudyVersion,
          click: this.editStudyActivity,
          accessRole: this.$roles.STUDY_WRITE,
        },
        {
          label: this.$t('DetailedFlowchart.add_activity'),
          icon: 'mdi-plus-circle-outline',
          condition: () => !this.selectedStudyVersion,
          click: this.addStudyActivity,
          accessRole: this.$roles.STUDY_WRITE,
        },
        {
          label: this.$t('DetailedFlowchart.exchange_activity'),
          icon: 'mdi-autorenew',
          condition: () => !this.selectedStudyVersion,
          click: this.exchangeStudyActivity,
          accessRole: this.$roles.STUDY_WRITE,
        },
        {
          label: this.$t('DetailedFlowchart.remove_activity'),
          icon: 'mdi-minus-circle-outline',
          condition: () => !this.selectedStudyVersion,
          click: this.removeActivity,
          accessRole: this.$roles.STUDY_WRITE,
        },
      ],
      showActivityEditForm: false,
      showDraftedActivityEditForm: false,
      selectedStudyActivity: null,
      activityExchangeMode: false,
      showActivityForm: false,
      flowchartActivityOrder: null
    }
  },
  computed: {
    numHeaderRows() {
      return this.soaContent ? this.soaContent.num_header_rows : 4
    },
    soaEpochRow() {
      if (this.soaContent) {
        return this.soaContent.rows[0].cells.slice(1)
      }
      return []
    },
    soaMilestoneRow() {
      if (this.soaContent && this.soaContent.num_header_rows > 4) {
        return this.soaContent.rows[1].cells.slice(1)
      }
      return []
    },
    soaVisitRow() {
      if (this.soaContent) {
        return this.soaContent.rows[
          this.soaContent.num_header_rows - 3
        ].cells.slice(1)
      }
      return []
    },
    soaDayRow() {
      if (this.soaContent) {
        return this.soaContent.rows[this.soaContent.num_header_rows - 2].cells
      }
      return []
    },
    soaWindowRow() {
      if (this.soaContent) {
        return this.soaContent.rows[
          this.soaContent.num_header_rows - 1
        ].cells
      }
      return []
    },
    soaRows() {
      if (this.soaContent) {
        return this.soaContent.rows.slice(this.soaContent.num_header_rows)
      }
      return []
    },
    thirdHeaderRowTop() {
      return (
        this.firstHeaderHeight +
        this.secondHeaderHeight +
        this.milestoneHeaderHeight
      )
    },
    fourthHeaderRowTop() {
      return (
        this.firstHeaderHeight +
        this.secondHeaderHeight +
        this.milestoneHeaderHeight +
        this.thirdHeaderHeight
      )
    },
    formattedStudyActivitySelection() {
      return this.studyActivitySelection.map((cell) => {
        return {
          study_activity_uid: cell.refs[0].uid,
          activity: { name: cell.text },
        }
      })
    },
    historyTitle() {
      return this.$t('DetailedFlowchart.history_title', {
        study: this.selectedStudy.uid,
      })
    },
    selectedVisits() {
      return this.selectedVisitIndexes.map((cell) => this.soaVisitRow[cell])
    }
  },
  watch: {
    redirectFootnote(value) {
      this.enableFootnoteMode(value)
    },
    update() {
      this.loadSoaContent()
    },
    '$route.params.footnote'(value) {
      if (value && !_isEmpty(value)) {
        this.enableFootnoteMode(value)
      }
    },
  },
  mounted() {
    this.loadSoaContent()
    this.onResize()
    this.fetchFootnotes()
    if (this.$route.params.footnote && !_isEmpty(this.$route.params.footnote)) {
      this.enableFootnoteMode(this.$route.params.footnote)
    }
  },
  updated() {
    this.observeWidth()
    if (!this.$refs.firstHeader) {
      return
    }
    this.firstHeaderHeight = this.$refs.firstHeader.clientHeight
    this.secondHeaderHeight = this.$refs.secondHeader.clientHeight
    this.thirdHeaderHeight = this.$refs.thirdHeader.clientHeight
    if (this.$refs.milestoneHeader) {
      this.milestoneHeaderHeight = this.$refs.milestoneHeader.clientHeight
    }
    this.firstColWidth = this.$refs.firstCol.clientWidth
    this.secondColWidth = this.$refs.secondCol.clientWidth
  },
  methods: {
    observeWidth() {
      const resizeObserver = new ResizeObserver(function(el) {
        if (el[0].target.offsetWidth && document.getElementById('bottomCard') && document.getElementById('bottomCard').style) {
          document.getElementById('bottomCard').style.left = el[0].target.offsetWidth + 'px'
        }
      })
      resizeObserver.observe(document.getElementById('sideBar'))
    },
    async removeActivity(activity) {
      const options = { type: 'warning' }
      if (!(await this.$refs.confirm.open(this.$t('DetailedFlowchart.remove_activity_msg'), options))) {
        return
      }
      this.loadingSoaContent = true
      study
        .deleteStudyActivity(this.selectedStudy.uid, activity.uid)
        .then(() => {
          this.eventBusEmit('notification', {
            type: 'success',
            msg: this.$t('DetailedFlowchart.remove_activity_success'),
          })
          this.loadSoaContent(true)
        })
    },
    addStudyActivity(item) {
      study
        .getStudyActivity(
          this.selectedStudy.uid,
          item.uid
        )
        .then((resp) => {
        this.flowchartActivityOrder = resp.data.order
        this.showActivityForm = true
        })
    },
    exchangeStudyActivity(item) {
      this.selectedStudyActivity = item.uid
      this.activityExchangeMode = true
      this.showActivityForm = true
    },
    closeActivityForm() {
      this.selectedStudyActivity = null
      this.activityExchangeMode = false
      this.flowchartActivityOrder = null
      this.showActivityForm = false
      this.loadSoaContent(true)
    },
    onActivityExchanged() {
      this.showActivityForm = false
      this.activityExchangeMode = false
      this.loadSoaContent(true)
    },
    editStudyActivity(item) {
      study
        .getStudyActivity(
          this.selectedStudy.uid,
          item.uid
        )
        .then((resp) => {
          this.selectedStudyActivity = resp.data
          if (resp.data.activity.library_name === libraries.LIBRARY_REQUESTED && !resp.data.activity.is_request_final) {
            this.showDraftedActivityEditForm = true
          } else {
            this.showActivityEditForm = true
          }
        })
    },
    closeEditForm() {
      this.showActivityEditForm = false
      this.showDraftedActivityEditForm = false
      this.selectedStudyActivity = null
    },
    openRemoveFootnoteForm(ele) {
      this.removeItemUid = ele.refs[0].uid
      this.showRemoveFootnoteForm = true
    },
    closeRemoveFootnoteForm() {
      this.removeItemUid = null
      this.showRemoveFootnoteForm = false
      this.loadSoaContent(true)
    },
    showSoaRow(index, row) {
      let key = `row-${index}`
      let result = true

      // prettier-ignore
      while (true) { // eslint-disable-line no-constant-condition
        if (
          this.rowsDisplayState[key] &&
          this.rowsDisplayState[key].parent !== undefined &&
          this.rowsDisplayState[key].parent !== null
        ) {
          const parentIndex = this.rowsDisplayState[key].parent
          key = `row-${parentIndex}`
          if (this.rowsDisplayState[key]) {
            // We want to check if parent is an soaGroup or not (not parent === soaGroup)
            if (!this.rowsDisplayState[key].value) {
              result = false
              break
            }
          } else {
            console.log(`Warning: key ${key} not found in displayState!!`)
          }
          continue
        }
        break
      }
      if (row.cells && row.cells.length) {
        if (row.cells[0].style === 'soaGroup') {
          return true
        }
        if (row.cells[0].style === 'group') {
          return result
        }
      }
      return result
    },
    getSoaRowType(row) {
      return row.cells[0].style
    },
    getSoaRowClasses(row) {
      if (row.cells && row.cells.length) {
        if (row.cells[0].style === 'soaGroup') {
          return 'flowchart'
        }
        if (row.cells[0].style === 'group') {
          return 'group'
        }
        if (row.cells[0].style === 'subGroup') {
          return 'subgroup'
        }
      }
      return 'bg-white'
    },
    getSoaFirstCellClasses(cell) {
      let result = 'sticky-column'
      if (cell.style === 'soaGroup' || cell.style === 'group') {
        result += ' text-strong'
      } else if (cell.style === 'subGroup') {
        result += ' subgroup'
      }
      return result
    },
    getStudyActivitiesForSoaGroup(soaGroupUid) {
      let groupFound = false
      const result = []
      for (const row of this.soaRows) {
        if (
          row.cells[0].style === 'soaGroup' &&
          row.cells[0].refs[0].uid === soaGroupUid
        ) {
          groupFound = true
        } else if (groupFound) {
          if (row.cells[0].style === 'activity') {
            result.push(row.cells[0])
          } else if (row.cells[0].style === 'soaGroup') {
            break
          }
        }
      }
      return result
    },
    getStudyActivitiesForGroup(groupUid) {
      let groupFound = false
      const result = []
      for (const row of this.soaRows) {
        if (
          row.cells[0].style === 'group' &&
          row.cells[0].refs?.[0]?.uid === groupUid
        ) {
          groupFound = true
        } else if (groupFound) {
          if (row.cells[0].style === 'activity') {
            result.push(row.cells[0])
          } else if (row.cells[0].style === 'group') {
            break
          }
        }
      }
      return result
    },
    getStudyActivitiesForSubgroup(subgroupUid) {
      let subgroupFound = false
      const result = []
      for (const row of this.soaRows) {
        if (
          row.cells[0].style === 'subGroup' &&
          row.cells[0].refs?.[0]?.uid === subgroupUid
        ) {
          subgroupFound = true
        } else if (subgroupFound) {
          if (row.cells[0].style === 'activity') {
            result.push(row.cells[0])
          } else {
            break
          }
        }
      }
      return result
    },
    getElementFootnotes(uid) {
      let footnotesLetters = []
      this.footnotesStore.studyFootnotes.forEach((footnote) => {
        footnote.referenced_items.forEach((item) => {
          if (item.item_uid === uid) {
            footnotesLetters.push({ order: dataFormating.letteredOrder(footnote.order), uid: footnote.uid })
          } else if (
            uid &&
            typeof uid !== 'string' &&
            uid.includes(item.item_uid)
          ) {
            footnotesLetters.push({ order: dataFormating.letteredOrder(footnote.order), uid: footnote.uid })
          }
        })
      })
      return footnotesLetters
    },
    getElementFootnotesLetters(uid) {
      let footnotesLetters = ''
      this.footnotesStore.studyFootnotes.forEach((footnote) => {
        footnote.referenced_items.forEach((item) => {
          if (item.item_uid === uid) {
            footnotesLetters += dataFormating.letteredOrder(footnote.order)
          } else if (
            uid &&
            typeof uid !== 'string' &&
            uid.includes(item.item_uid)
          ) {
            footnotesLetters += dataFormating.letteredOrder(footnote.order)
          }
        })
      })
      return Array.from(new Set(footnotesLetters.split(''))).toString()
    },
    enableFootnoteMode(footnote) {
      if (footnote) {
        this.activeFootnote = footnote
        this.elementsForFootnote.referenced_items = footnote.referenced_items
      }
      this.footnoteMode = true
    },
    enableFootnoteModeWithElement(uid, type, name) {
      this.elementsForFootnote.referenced_items.push({
        item_uid: uid,
        item_type: type,
        item_name: name,
      })
      this.footnoteMode = true
    },
    disableFootnoteMode() {
      if (this.$route.params.footnote) {
        this.$router.push({
          name: 'StudyActivities',
          params: { tab: 'footnotes' },
        })
        this.$route.params.footnote = null
      }
      this.activeFootnote = null
      this.elementsForFootnote.referenced_items = []
      this.footnoteMode = false
      this.fetchFootnotes()
    },
    addElementForFootnote(uid, type, name) {
      if (!name) {
        name = type
      }
      if (typeof uid !== 'string') {
        uid.forEach((u) => {
          this.elementsForFootnote.referenced_items.push({
            item_uid: u,
            item_type: type,
            item_name: name,
          })
        })
      } else {
        this.elementsForFootnote.referenced_items.push({
          item_uid: uid,
          item_type: type,
          item_name: name,
        })
      }
    },
    removeFootnote(uid) {
      const indexToRemove = this.elementsForFootnote.referenced_items.findIndex(
        (item) => item.item_uid === uid
      )
      if (indexToRemove !== -1) {
        this.elementsForFootnote.referenced_items.splice(indexToRemove, 1)
      }
    },
    removeElementForFootnote(uid) {
      if (typeof uid !== 'string') {
        uid.forEach((u) => {
          this.removeFootnote(u)
        })
      } else {
        this.removeFootnote(uid)
      }
    },
    saveElementsForFootnote() {
      if (this.activeFootnote) {
        this.footnoteUpdateLoading = true
        study
          .updateStudyFootnote(
            this.selectedStudy.uid,
            this.activeFootnote.uid,
            this.elementsForFootnote
          )
          .then(() => {
            this.footnoteUpdateLoading = false
            this.disableFootnoteMode()
            this.loadSoaContent(true)
            this.eventBusEmit('notification', {
              msg: this.$t('StudyFootnoteEditForm.update_success'),
            })
          })
      } else {
        this.showFootnoteForm = true
      }
    },
    closeFootnoteForm() {
      this.showFootnoteForm = false
      this.disableFootnoteMode()
    },
    checkIfElementHasFootnote(elUid) {
      if (elUid && typeof elUid === 'string') {
        return this.elementsForFootnote.referenced_items.find(
          (item) => item.item_uid === elUid
        )
      } else if (elUid) {
        return this.elementsForFootnote.referenced_items.find(
          (item) => item.item_uid === elUid[0]
        )
      }
    },
    fetchFootnotes() {
      const params = {
        page_number: 1,
        page_size: 0,
        total_count: true,
        studyUid: this.selectedStudy.uid,
      }
      this.footnotesStore.fetchStudyFootnotes(params)
    },
    isCheckboxDisabled(studyActivityUid, studyVisitUid) {
      const state = this.currentSelectionMatrix[studyActivityUid][studyVisitUid]
      return (
        this.readOnly ||
        (state.value && !state.uid) ||
        (!state.value && state.uid !== null)
      )
    },
    getCurrentDisplayValue(rowKey) {
      const currentValue = this.rowsDisplayState[rowKey].value
      if (currentValue === undefined) {
        return false
      }
      return currentValue
    },
    getDisplayButtonIcon(rowKey) {
      return this.getCurrentDisplayValue(rowKey)
           ? 'mdi-chevron-down'
           : 'mdi-chevron-right'
    },
    getLevelDisplayState(row) {
      return !row.hide
    },
    toggleRowState(rowKey) {
      const currentValue = this.getCurrentDisplayValue(rowKey)
      this.rowsDisplayState[rowKey].value = !currentValue
    },
    toggleAllRowState(value) {
      for (const key in this.rowsDisplayState) {
        this.rowsDisplayState[key].value = value
      }
    },
    toggleActivitySelection(row, value) {
      const activityCell = row.cells[0]
      if (value) {
        this.studyActivitySelection.push(activityCell)
      } else {
        for (let i = 0; i < this.studyActivitySelection.length; i++) {
          if (
            this.studyActivitySelection[i].refs[0].uid ===
              activityCell.refs[0].uid
          ) {
            this.studyActivitySelection.splice(i, 1)
            break
          }
        }
      }
    },
    async updateStudyActivity(studyActivityCell, data) {
      await study.updateStudyActivity(
        this.selectedStudy.uid,
        studyActivityCell.refs[0].uid,
        data
      )
    },
    async toggleLevelDisplay(row) {
      const firstCell = row.cells[0]
      let action
      let field

      if (firstCell.style === 'activity') {
        field = 'show_activity_in_protocol_flowchart'
        action = 'updateStudyActivity'
      } else if (firstCell.style === 'subGroup') {
        field = 'show_activity_subgroup_in_protocol_flowchart'
        action = 'updateStudyActivitySubGroup'
      } else if (firstCell.style === 'group') {
        field = 'show_activity_group_in_protocol_flowchart'
        action = 'updateStudyActivityGroup'
      } else if (firstCell.style === 'soaGroup') {
        field = 'show_soa_group_in_protocol_flowchart'
        action = 'updateStudySoaGroup'
      }
      const payload = {}
      payload[field] = row.hide
      await study[action](
        this.selectedStudy.uid,
        firstCell.refs[0].uid,
        payload
      )
      row.hide = !row.hide
    },
    updateGroupedSchedule(value, studyActivityUid, studyVisitCell) {
      if (value) {
        const data = []
        for (const visitRef of studyVisitCell.refs) {
          data.push({
            method: 'POST',
            content: {
              study_activity_uid: studyActivityUid,
              study_visit_uid: visitRef.uid,
            },
          })
        }
        study
          .studyActivityScheduleBatchOperations(this.selectedStudy.uid, data)
          .then((resp) => {
            const scheduleUids = resp.data.map(
              (item) => item.content.study_activity_schedule_uid
            )
            this.currentSelectionMatrix[studyActivityUid][
              studyVisitCell.refs[0].uid
            ].uid = scheduleUids
          })
      } else {
        const data = []
        for (const scheduleUid of this.currentSelectionMatrix[studyActivityUid][
          studyVisitCell.refs[0].uid
        ].uid) {
          data.push({
            method: 'DELETE',
            content: {
              uid: scheduleUid,
            },
          })
        }
        study
          .studyActivityScheduleBatchOperations(this.selectedStudy.uid, data)
          .then(() => {
            this.currentSelectionMatrix[studyActivityUid][
              studyVisitCell.refs[0].uid
            ].uid = null
          })
      }
    },
    updateSchedule(value, studyActivityUid, studyVisitCell) {
      if (studyVisitCell.refs.length > 1) {
        this.updateGroupedSchedule(value, studyActivityUid, studyVisitCell)
        return
      }
      if (value) {
        const data = {
          study_activity_uid: studyActivityUid,
          study_visit_uid: studyVisitCell.refs[0].uid,
        }
        study
          .createStudyActivitySchedule(this.selectedStudy.uid, data)
          .then((resp) => {
            this.currentSelectionMatrix[studyActivityUid][
              studyVisitCell.refs[0].uid
            ].uid = resp.data.study_activity_schedule_uid
          })
      } else {
        const scheduleUid =
          this.currentSelectionMatrix[studyActivityUid][
            studyVisitCell.refs[0].uid
          ].uid
        study
              .deleteStudyActivitySchedule(this.selectedStudy.uid, scheduleUid)
              .then(() => {
                this.currentSelectionMatrix[studyActivityUid][
                  studyVisitCell.refs[0].uid
                ].uid = null
              })
      }
    },
    async openBatchEditForm() {
      if (!this.studyActivitySelection.length) {
        this.eventBusEmit('notification', {
          type: 'warning',
          msg: this.$t('DetailedFlowchart.batch_edit_no_selection'),
        })
        return
      }
      this.showBatchEditForm = true
    },
    unselectItem(item) {
      this.studyActivitySelection = this.studyActivitySelection.filter(
        (sa) => sa.refs[0].uid !== item.study_activity_uid
      )
    },
    async batchRemoveStudyActivities() {
      if (!this.studyActivitySelection.length) {
        this.eventBusEmit('notification', {
          type: 'warning',
          msg: this.$t('DetailedFlowchart.batch_remove_no_selection'),
        })
        return
      }
      const data = []
      for (const cell of this.studyActivitySelection) {
        data.push({
          method: 'DELETE',
          content: {
            study_activity_uid: cell.refs[0].uid,
          },
        })
      }
      const options = { type: 'warning' }
      if (!(await this.$refs.confirm.open(this.$t('DetailedFlowchart.remove_multiple_activities_msg', {activities: this.studyActivitySelection.length}), options))) {
        return
      }
      this.loadingSoaContent = true
      study
        .studyActivityBatchOperations(this.selectedStudy.uid, data).then(() => {
          this.eventBusEmit('notification', {
            msg: this.$t('DetailedFlowchart.remove_success', {activities: this.studyActivitySelection.length}),
          })
          this.studyActivitySelection = []
          this.loadSoaContent(true)
        })
    },
    toggleActivitySelectionDisplay(value) {
      if (!this.studyActivitySelection.length) {
        this.eventBusEmit('notification', {
          type: 'warning',
          msg: this.$t('DetailedFlowchart.batch_edit_no_selection'),
        })
        return
      }
      const data = []
      for (const cell of this.studyActivitySelection) {
        data.push({
          method: 'PATCH',
          content: {
            study_activity_uid: cell.refs[0].uid,
            content: {
              show_activity_in_protocol_flowchart: value,
            },
          },
        })
      }
      study
        .studyActivityBatchOperations(this.selectedStudy.uid, data)
        .then(() => {
          this.eventBusEmit('notification', {
            type: 'success',
            msg: this.$t('DetailedFlowchart.update_success'),
          })
          this.loadSoaContent(true)
        })
    },
    toggleSubgroupActivitiesSelection(subgroupRow, value) {
      const activityCells = this.getStudyActivitiesForSubgroup(
        subgroupRow.cells[0].refs?.[0]?.uid
      )
      if (value) {
        this.studyActivitySelection =
          this.studyActivitySelection.concat(activityCells)
      } else {
        for (const activityCell of activityCells) {
          const index = this.studyActivitySelection.findIndex(
            (cell) => cell.refs?.[0]?.uid === activityCell.refs?.[0]?.uid
          )
          this.studyActivitySelection.splice(index, 1)
        }
      }
    },
    async loadSoaContent(keepDisplayState) {
      this.loadingSoaContent = true
      this.soaContentLoadingStore.changeLoadingState()
      this.studyActivitySelection = []
      try {
        const resp = await study.getStudyProtocolFlowchart(
          this.selectedStudy.uid,
          { detailed: true }
        )
        this.soaContent = resp.data
      } catch {
        this.loadingSoaContent = false
      }
      let currentSoaGroup
      let currentGroup
      let currentSubGroup

      if (!keepDisplayState) {
        this.rowsDisplayState = {}
        this.expandAllRows = false
      }
      for (const [index, row] of this.soaRows.entries()) {
        const key = `row-${index}`
        if (row.cells && row.cells.length) {
          if (row.cells[0].style === 'soaGroup') {
            if (!keepDisplayState) {
              this.rowsDisplayState[key] = { value: false }
            }
            currentGroup = null
            currentSubGroup = null
            currentSoaGroup = index
          } else if (row.cells[0].style === 'group') {
            if (!keepDisplayState) {
              this.rowsDisplayState[key] = {
                value: false,
                parent: currentSoaGroup,
              }
            }
            currentSubGroup = null
            currentGroup = index
          } else if (row.cells[0].style === 'subGroup') {
            if (!keepDisplayState) {
              this.rowsDisplayState[key] = {
                value: false,
                parent: currentGroup,
              }
            }
            currentSubGroup = index
          } else if (row.cells[0].style === 'activity') {
            const scheduleCells = row.cells.slice(1)
            if (!keepDisplayState) {
              this.rowsDisplayState[key] = {
                value: false,
                parent: currentSubGroup,
              }
            }
            if (row.cells[0].refs && row.cells[0].refs.length) {
              this.currentSelectionMatrix[row.cells[0].refs?.[0].uid] = {}
              for (const [visitIndex, cell] of this.soaVisitRow.entries()) {
                let props
                if (
                  scheduleCells[visitIndex].refs &&
                  scheduleCells[visitIndex].refs.length
                ) {
                  if (cell.refs && cell.refs.length === 1) {
                    props = {
                      value: true,
                      uid: scheduleCells[visitIndex].refs[0].uid,
                    }
                  } else {
                    props = {
                      value: true,
                      uid: scheduleCells[visitIndex].refs.map((ref) => ref.uid),
                    }
                  }
                } else {
                  props = { value: false, uid: null }
                }
                if (cell.refs) {
                  this.currentSelectionMatrix[row.cells[0].refs[0].uid][
                    cell.refs[0].uid
                  ] = props
                }
              }
            }
          }
        }
      }
      this.loadingSoaContent = false
      this.soaContentLoadingStore.changeLoadingState()
    },
    onResize() {
      this.tableHeight =
        window.innerHeight -
        this.$refs.tableContainer.getBoundingClientRect().y -
        100
    },
    groupSelectedVisits() {
      const visitUids = this.selectedVisitIndexes.map(
        (cell) => this.soaVisitRow[cell].refs[0].uid
      )
      studyEpochs
        .createCollapsibleVisitGroup(this.selectedStudy.uid, visitUids)
        .then(() => {
          this.collapsibleVisitGroupCreated()
        })
        .catch((err) => {
          if (err.response.status === 400) {
            if (err.response.data.type !== 'BusinessLogicException') {
              this.showCollapsibleGroupForm = true
            } else {
              this.eventBusEmit('notification', {
                msg: err.response.data.message,
                type: 'error',
              })
            }
          }
        })
    },
    closeCollapsibleVisitGroupForm() {
      this.showCollapsibleGroupForm = false
    },
    collapsibleVisitGroupCreated() {
      this.eventBusEmit('notification', {
        msg: this.$t('CollapsibleVisitGroupForm.creation_success'),
      })
      this.loadSoaContent(true)
      this.selectedVisitIndexes = []
    },
    async deleteVisitGroup(groupName) {
      const message = this.$t('DetailedFlowchart.confirm_group_deletion', {
        group: groupName,
      })
      const options = { type: 'warning' }
      if (!(await this.$refs.confirm.open(message, options))) {
        return
      }
      await studyEpochs.deleteCollapsibleVisitGroup(
        this.selectedStudy.uid,
        groupName
      )
      this.loadSoaContent(true)
    },
    async getHistoryData(options) {
      const params = {
        total_count: true,
      }
      if (options) {
        params.page_number = options.page ? options.page : 1
        params.page_size = options.itemsPerPage ? options.itemsPerPage : 10
      }
      const resp = await study.getStudySoAHistory(
        this.selectedStudy.uid,
        params
      )
      this.historyItems = resp.data.items
      this.historyItemsTotal = resp.data.total
    },
    async openHistory() {
      await this.getHistoryData()
      this.showHistory = true
    },
    closeHistory() {
      this.showHistory = false
    },
    async downloadCSV() {
      this.soaContentLoadingStore.changeLoadingState()
      try {
        await soaDownloads.csvDownload('detailed')
      } finally {
        this.soaContentLoadingStore.changeLoadingState()
      }
    },
    async downloadEXCEL() {
      this.soaContentLoadingStore.changeLoadingState()
      try {
        await soaDownloads.excelDownload('detailed')
      } finally {
        this.soaContentLoadingStore.changeLoadingState()
      }
    },
    async downloadDOCX() {
      this.soaContentLoadingStore.changeLoadingState()
      try {
        await soaDownloads.docxDownload('detailed')
      } finally {
        this.soaContentLoadingStore.changeLoadingState()
      }
    },
    multipleConsecutiveVisitsSelected() {
      // Check if more than one visit is selected,
      // and that they are in consecutive order without gaps.
      if (this.selectedVisitIndexes.length > 1) {
        const minIndex = this.selectedVisitIndexes.reduce((a, b) =>
          Math.min(a, b)
        )
        const maxIndex = this.selectedVisitIndexes.reduce((a, b) =>
          Math.max(a, b)
        )
        return this.selectedVisitIndexes.length - 1 === maxIndex - minIndex
      }
      return false
    },
  },
}
</script>

<style lang="scss" scoped>
 table {
   width: 100%;
   text-align: left;
   border-spacing: 0px;
   border-collapse: collapse;
 }
 thead {
   background-color: rgb(var(--v-theme-tableGray));
   font-weight: 600;
 }
 tr {
   padding: 4px;
   &.section {
     background-color: rgb(var(--v-theme-tableGray));
     font-weight: 600;
   }
 }
 tbody tr {
   border-bottom: 1px solid rgb(var(--v-theme-greyBackground));
 }
 th {
   vertical-align: bottom;
   background-color: rgb(var(--v-theme-nnLightBlue100));
   min-width: 120px;
 }
 th,
 td {
   position: relative;
   padding: 6px;
   font-size: 14px;
   z-index: 0;
 }

 td {
   background-color: inherit;
 }

 .sticky-header {
   overflow-y: auto;

   thead th {
     position: sticky;
     top: 0;
     z-index: 3;
   }
 }
 .sticky-column {
   position: sticky;
   left: 0px;
   z-index: 4 !important;
 }
 .header {
   background-color: rgb(var(--v-theme-nnTrueBlue));
   color: rgb(var(--v-theme-nnWhite));
   z-index: 10;
   left: 0px;
 }
 .zindex25 {
   z-index: 25 !important;
 }
 .bottomCard {
   align-content: center;
   position: fixed;
   bottom: 0;
   z-index: 1100;
   height: 100px;
   width: -webkit-fill-available;
 }
 .flowchart {
   background-color: rgb(var(--v-theme-nnSeaBlue300));
 }
 .group {
   background-color: rgb(var(--v-theme-nnSeaBlue200));
 }
 .subgroup {
   background-color: rgb(var(--v-theme-nnSeaBlue100));
   font-weight: 600;
 }
 .text-strong {
   font-weight: 600;
 }
 .visitFootnote {
   margin-bottom: 8px;
 }
 .layoutSelector {
   border-color: rgb(var(--v-theme-nnBaseBlue));
 }
 .v-card-text {
   display: inline-flex;
 }
</style>
