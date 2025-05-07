<template>
  <div>
    <b-card title="Settings">
      <b-row>
        <b-col class="d-flex align-items-center">
          <b-form-radio-group
            v-model="settings.visualization"
            text-field="label"
            :options="visualizationOptions"/>
            <div>
              <b-dropdown variant="primary" text="Preset" right>
                <b-dropdown-item 
                  v-for="preset in presets"
                  :key="preset"
                  @click="setPresetValues(preset)">
                  {{ preset.label }}
                </b-dropdown-item>
                <!-- <b-dropdown-divider />
                <b-dropdown-item>Add as preset</b-dropdown-item> -->
              </b-dropdown>
            </div>
          </b-col>
      </b-row>
      <b-row class="mt-3">
        <b-col cols="4" lg="2" xl="1">
          <b-form-group
            label="Width:">
            <b-form-input type="number" min="1" v-model.number="settings.width" />
          </b-form-group>
        </b-col>
        <b-col cols="4" lg="2" xl="1">
          <b-form-group
            label="Height:">
            <b-form-input type="number" min="1" v-model.number="settings.height" />
          </b-form-group>
        </b-col>
        <b-col cols="4" lg="2" xl="1">
          <b-form-group
            label="Framerate:">
            <b-form-input type="number" min="1" v-model.number="settings.framerate" />
          </b-form-group>
        </b-col>
        <b-col cols="8" lg="4" xl="2">
          <b-row>
            <b-col cols="6">
              <b-form-group
                label="Audio Start:">
                <b-form-input type="number" min="0" :max="settings.startEnd[1]" v-model.number="settings.startEnd[0]" />
              </b-form-group>
            </b-col>
            <b-col cols="6">
              <b-form-group
                label="Audio End:">
                <b-form-input type="number" :min="settings.startEnd[0]" :max="Math.floor(audioDuration)" v-model.number="settings.startEnd[1]" />
              </b-form-group>
            </b-col>
            <b-col cols="11" class="mx-auto">
              <Slider
                @slide="settings.startEnd = $event"
                v-model="settings.startEnd"
                :disabled="!audioDuration"
                :min="0" :max="Math.floor(audioDuration)"
                :step="1"
                :tooltips="false"
                class="slider-blue" />
            </b-col>
          </b-row>
        </b-col>
        <b-col cols="8" lg="4" xl="2">
          <b-row>
            <b-col cols="6">
              <b-form-group
                label="Frequency Start:">
                <b-form-input type="number" step="100" min="0" :max="settings.minMaxFrequency[1]" v-model.number="settings.minMaxFrequency[0]" />
              </b-form-group>
            </b-col>
            <b-col cols="6">
              <b-form-group
                label="Frequency End:">
                <b-form-input type="number" step="100" :min="settings.minMaxFrequency[0]" max="22050" v-model.number="settings.minMaxFrequency[1]" />
              </b-form-group>
            </b-col>
            <b-col cols="11" class="mx-auto">
              <Slider
                @slide="settings.minMaxFrequency = $event"
                v-model="settings.minMaxFrequency"
                :min="0" :max="22050"
                :step="100"
                :tooltips="false"
                class="slider-blue" />
            </b-col>
          </b-row>
        </b-col>
        <b-col cols="8" lg="4" xl="2">
          <b-form-group
            label="Output Filename:">
            <b-form-input :disabled="!audioFileName" type="text" v-model="settings.fileName" />
          </b-form-group>
        </b-col>
      </b-row>
      <b-row class="mt-3">
        <b-col cols="4" lg="2" xl="1" v-if="settings.visualization === 'spectrum'">
          <b-form-group
            label="Style:">
            <b-form-select v-model="settings.style" :options="styleOptions" text-field="label" />
          </b-form-group>
        </b-col>
        <b-col cols="4" lg="2" xl="1" v-if="settings.visualization === 'spectrum'">
          <b-form-group
            label="Variant:">
            <b-form-select v-model="settings.styleVariant" :options="styleVariantOptions[settings.style]" text-field="label" />
          </b-form-group>
        </b-col>
        <b-col cols="4" lg="2" xl="1">
          <b-form-group
            label="Color:">
            <b-form-input type="color" v-model="settings.color" class="w-100" />
          </b-form-group>
        </b-col>
        <b-col cols="4" lg="2" xl="1">
          <b-form-group
            label="Background:">
            <b-form-input type="color" v-model="settings.backgroundColor" class="w-100" />
          </b-form-group>
        </b-col>
        <b-col cols="4" lg="2" xl="1" v-if="settings.visualization === 'spectrum'">
          <b-form-group
            label="Bins:">
            <b-form-input type="number" min="1" v-model.number="settings.bins" />
          </b-form-group>
        </b-col>
        <b-col cols="4" lg="2" xl="1" v-if="settings.visualization === 'spectrum' && settings.style !== 'line'">
          <b-row>
            <b-col cols="12">
              <b-form-group
              label="Bin Width:">
                <b-form-input type="number" min="0.01" max="1" step="0.01" v-model.number="settings.binWidth" />
            </b-form-group>
            </b-col>
            <b-col cols="11" class="mx-auto">
              <Slider
                @slide="settings.binWidth = $event"
                v-model="settings.binWidth"
                :min="0.01" :max="1"
                :step="0.01"
                :tooltips="false"
                class="slider-blue" />
            </b-col>
          </b-row>
        </b-col>
        <b-col cols="4" lg="2" xl="1" v-if="settings.visualization === 'spectrum' && settings.style === 'line' && settings.styleVariant === 'simple'">
          <b-row>
            <b-col cols="12">
              <b-form-group
              label="Line Thickness:">
                <b-form-input type="number" min="1" max="20" step="1" v-model.number="settings.lineThickness" />
            </b-form-group>
            </b-col>
            <b-col cols="11" class="mx-auto">
              <Slider
                @slide="settings.lineThickness = $event"
                v-model="settings.lineThickness"
                :min="1" :max="20"
                :step="1"
                :tooltips="false"
                class="slider-blue" />
            </b-col>
          </b-row>
        </b-col>
        <b-col cols="8" lg="4" xl="2" v-if="settings.visualization === 'volume' || settings.polarWarp">
          <b-row>
            <b-col cols="6">
              <b-form-group
                label="Inner Radius:">
                <b-form-input type="number" step="0.01" min="0" :max="settings.innerOuterRadius[1]" v-model.number="settings.innerOuterRadius[0]" />
              </b-form-group>
            </b-col>
            <b-col cols="6">
              <b-form-group
                label="Outer Radius:">
                <b-form-input type="number" step="0.01" :min="settings.innerOuterRadius[0]" max="1" v-model.number="settings.innerOuterRadius[1]" />
              </b-form-group>
            </b-col>
            <b-col cols="11" class="mx-auto">
              <Slider
                @slide="settings.innerOuterRadius = $event"
                v-model="settings.innerOuterRadius"
                :min="0" :max="1"
                :step="0.01"
                :tooltips="false"
                class="slider-blue" />
            </b-col>
          </b-row>
        </b-col>
      </b-row>
      <b-row class="mt-3">
        <b-col cols="4" lg="2" xl="1">
          <b-form-group
            label="Smoothing:">
            <b-form-checkbox v-model="settings.smoothing" />
          </b-form-group>
        </b-col>
        <b-col cols="4" lg="2" xl="1">
          <b-form-group
            label="Anti-aliasing:">
            <b-form-checkbox v-model="settings.antiAliasing" />
          </b-form-group>
        </b-col>
        <b-col cols="4" lg="2" xl="1">
          <b-form-group
            label="Polar Warp:">
            <b-form-checkbox v-model="settings.polarWarp" />
          </b-form-group>
        </b-col>
      </b-row>
    </b-card>
  </div>
</template>

<script>
import '@vueform/slider/themes/default.css'
import Slider from '@vueform/slider'

export default {
  components: {
    Slider
  },
  data() {
    return {
      presets: [
        {
          label: "Default",
          settings: {style: "bar", styleVariant: "simple", bins: 64, binWidth: 0.5, color: "#ffffff", backgroundColor: "#000000"},
        },
        {
          label: "IKEA",
          settings: {style: "bar", styleVariant: "simple", bins: 12, binWidth: 0.75, color: "#ffff00", backgroundColor: "#0000ff"},
        },
        {
          label: "Dunkin' Donuts",
          settings: {style: "point", styleVariant: "donut", bins: 16, binWidth: 0.75, color: "#e9388c", backgroundColor: "#f17e06"},
        },
        {
          label: "Hackerman",
          settings: {style: "line", styleVariant: "simple", lineThickness: 2, color: "#00ff00", backgroundColor: "#000000"},
        },
      ],
      settings: {
        visualization: "spectrum",
        style: "bar",
        styleVariant: "simple",
        fileName: "",
        width: 854,
        height: 480,
        framerate: 30,
        startEnd: [0, 0],
        smoothing: true,
        antiAliasing: true,
        polarWarp: false,
        bins: 64,
        binWidth: 0.5,
        lineThickness: 2,
        minMaxFrequency: [0, 4000],
        color: "#ffffff",
        backgroundColor: "#000000",
        innerOuterRadius: [0, 1],
      },
      visualizationOptions: [
        { label:"Spectrum", value: "spectrum" },
        { label:"Volume", value: "volume" },
      ],
      styleOptions: [
        { label:"Bar", value: "bar" },
        { label:"Point", value: "point" },
        { label:"Line", value: "line" },
      ],
      styleVariantOptions : {
        bar: [
          { label:"Simple", value: "simple" },
          { label:"LCD", value: "lcd" },
        ],
        point: [
          { label:"Circle", value: "circle" },
          { label:"Square", value: "square" },
          { label:"Donut", value: "donut" },
        ],
        line: [
          { label:"Simple", value: "simple" },
          { label:"Filled", value: "filled" },
        ],
      },
    }
  },
  props: {
    audioDuration: {
      type: Number,
    },
    audioSelection: {
      type: String,
    },
    audioFileName: {
      type: String,
    },
  },
  watch: {
    settings: {
      handler () {
        this.$emit('settings-changed', this.settings)
      },
      deep: true,
      immediate: true,
    },
    "settings.style": {
      handler () {
        if (this.settings.style === "bar") {
          this.settings.styleVariant = "simple"
        }
        if (this.settings.style === "point") {
          this.settings.styleVariant = "circle"
        }
        if (this.settings.style === "line") {
          this.settings.styleVariant = "simple"
        }
      }
    },
    audioDuration: {
      handler () {
        this.settings.startEnd = [0, Math.ceil(this.audioDuration)]
      },
    },
    audioFileName: {
      handler () {
        if (this.audioSelection === "file") {
          this.settings.fileName = this.audioFileName.slice(0, this.audioFileName.lastIndexOf("."))
        }
        if (this.audioSelection === "url") {
          this.settings.fileName = this.audioFileName
        }
      },
    },
  },
  methods: {
    setPresetValues (preset) {
      Object.assign(this.settings, preset.settings)
    },
  },
}
</script>

<style scoped>
.slider-blue {
  --slider-connect-bg: var(--bs-primary);
  --slider-connect-bg-disabled: var(--bs-primary-bg-subtle);
  --slider-handle-ring-width: 3px;
  --slider-handle-ring-color: rgba(var(--bs-primary-rgb), 0.2);
}
</style>

