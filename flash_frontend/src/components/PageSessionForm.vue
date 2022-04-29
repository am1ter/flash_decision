<template>
    <section id="page">
        <ModeSelector :page="'session'"/>

        <!-- Countdown for presets starts before form loading -->
        <countdown v-if="mode != 'custom'" 
            ref="pageTimer" 
            id="page-timer"
            :autoStart="true" 
            :left-time="5000"
            @finish="goToDecisions()">
            <template v-slot:process="pageTimer">
                <span v-if="pageTimer.timeObj.ceil.s > 3">Ready</span>
                <span v-if="pageTimer.timeObj.ceil.s > 1 && pageTimer.timeObj.ceil.s <= 3">Set</span>
                <span v-if="pageTimer.timeObj.ceil.s <= 1">Go!</span>
                <span id="page-timer-countdown">{{ `Session will start in ${pageTimer.timeObj.ceil.s}` }} sec.</span>
            </template>
            <template v-slot:finish>
                <span>Please wait. Session is starting</span>
            </template>
        </countdown>

        <form @submit.prevent="checkForm" autocomplete="off" v-if="apiErrors == 0 & !isLoading">
            <b-container class="g-0">
                <b-row cols="2" class="gx-0">
                    <!-- Parameters: b-col #1 - label, b-col #2 - custom mode, b-col #3 - all other modes -->
                    <b-col class="my-auto col-4">
                        <label>Market</label>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode == 'custom'">
                        <Dropdown 
                            name="input-market"
                            :class="checkClassIsInputInvalid('input-market')"
                            :options="sessionOptionsAll.markets"
                            :maxItem="inputMarketsLen"
                            v-on:selected="updateInputTickers"
                            placeholder="Select a securities market">
                        </Dropdown>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode != 'custom'">
                        <b-form-input disabled :value="currentSession['options']['aliases']['market']"></b-form-input>
                    </b-col>

                    <div class="w-100 my-1"></div>

                    <b-col class="my-auto col-4">
                        <label>Ticker</label>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode == 'custom'">
                        <Dropdown 
                            name="input-ticker"
                            :class="checkClassIsInputInvalid('input-ticker')"
                            :options="sessionOptionsTickers"
                            :maxItem="inputTickersLen"
                            placeholder="Select a security">
                        </Dropdown>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode != 'custom'">
                        <b-form-input disabled :value="currentSession['options']['aliases']['ticker']"></b-form-input>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto col-4">
                        <label>Timeframe</label>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode == 'custom'">
                        <Dropdown
                            name="input-timeframe"
                            :class="checkClassIsInputInvalid('input-timeframe')"
                            :options="sessionOptionsAll.timeframes"
                            :maxItem="7"
                            placeholder="Select a timeframe">
                        </Dropdown>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode != 'custom'">
                        <b-form-input disabled :value="currentSession['options']['aliases']['timeframe']"></b-form-input>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto col-4">
                        <label>Bars number</label>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode == 'custom'">
                        <Dropdown 
                            name="input-barsnumber"
                            :class="checkClassIsInputInvalid('input-barsnumber')"
                            :options="sessionOptionsAll.barsnumber"
                            placeholder="Select a number of bars">
                        </Dropdown>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode != 'custom'">
                        <b-form-input disabled :value="currentSession['options']['aliases']['barsnumber']"></b-form-input>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto col-4">
                        <label>Time limit</label>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode == 'custom'">
                        <Dropdown 
                            name="input-timelimit"
                            :class="checkClassIsInputInvalid('input-timelimit')"
                            :options="sessionOptionsAll.timelimit"
                            placeholder="Select a session time limit">
                        </Dropdown>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode != 'custom'">
                        <b-form-input disabled :value="currentSession['options']['aliases']['timelimit']"></b-form-input>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto col-4">
                        <label>Date</label>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode == 'custom'">
                        <b-form-datepicker 
                            id="input-date" 
                            name="input-date"
                            size="sm"
                            placeholder="Select a start date"
                            :class="checkClassIsInputInvalid('input-date')"
                            :date-format-options="{ 
                                year: 'numeric', month: 'numeric', day: 'numeric',
                                hour: 'numeric', minute: 'numeric', weekday: 'short'
                            }"
                            :min="dateMin"
                            :max="dateMax"
                            :date-disabled-fn="dateDisabled"
                            start-weekday=1
                            locale="ru">
                        </b-form-datepicker>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode != 'custom'">
                        <b-form-input disabled :value="currentSession['options']['aliases']['date']"></b-form-input>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto col-4">
                        <label>Iterations</label>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode == 'custom'">
                        <Dropdown 
                            name="input-iterations"
                            :class="checkClassIsInputInvalid('input-iterations')"
                            :options="sessionOptionsAll.iterations"
                            placeholder="Select a number of iterations">
                        </Dropdown>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode != 'custom'">
                        <b-form-input disabled :value="currentSession['options']['aliases']['iterations']"></b-form-input>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto col-4">
                        <label>Slippage</label>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode == 'custom'">
                        <Dropdown 
                            name="input-slippage"
                            :class="checkClassIsInputInvalid('input-slippage')"
                            :options="sessionOptionsAll.slippage"
                            placeholder="Select a slippage level">
                        </Dropdown>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode != 'custom'">
                        <b-form-input disabled :value="currentSession['options']['aliases']['slippage']"></b-form-input>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto col-4">
                        <label>Fixing bar</label>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode == 'custom'">
                        <Dropdown 
                            name="input-fixingbar"
                            :class="checkClassIsInputInvalid('input-fixingbar')"
                            :options="sessionOptionsAll.fixingbar"
                            placeholder="Select a result fixing bar">
                        </Dropdown>
                    </b-col>
                    <b-col class="my-auto col-8" v-if="mode != 'custom'">
                        <b-form-input disabled :value="currentSession['options']['aliases']['fixingbar']"></b-form-input>
                    </b-col>
                </b-row>
                <!-- Start button -->
                <b-button id="button-start" type="submit" squared class="col-12 mt-3 gradient">Start</b-button>
            </b-container>
        </form>
    </section>
</template>

<script>

    import { mapState, mapMutations } from "vuex"
    import { apiGetSessionOptions, apiPostStartNewSession } from "@/api"

    // Page subcomponents
    import ModeSelector from "./subcomponents/ModeSelector.vue"

    export default {
        name: "PageSessionForm",
        props: {},
        components: {
            ModeSelector
        },
        data() {
            return {
                sessionOptionsAll: [],
                inputMarketsLen: 10,
                sessionOptionsTickers: [],
                inputTickersLen: 10,
                selectedMarket: "SHARES",
                dateMax: new Date(),
                dateMin: new Date(2019, 0, 1),
                formErrors: [],
                mode: this.$route.params.mode
                }
        },
        computed: {
            ...mapState(["user", "currentSession", "apiErrors", "isLoading"])
        },
        beforeRouteUpdate(to, from, next) {
            // Ask for confirm before mode changing
            let answer = window.confirm("Do you really want to switch to another mode?")
            if (answer) {
                this.mode = to.params.mode
                this.prepareSession()         
                next()
            }
        },
        async beforeMount() {
            // Start page loading
            this.startLoading()
            // Create new session
            await this.prepareSession() 
            // Display page
            this.stopLoading()
        },
        methods: {
            ...mapMutations(["startLoading", "stopLoading"]),
            cleanResults() {
                // Clean results of previeous sessions
                this.currentSession["sessionsResults"] = {}
            },
            async prepareSession() {
                // Call functions to prepare page with session settings
                if (this.mode == "custom") {
                    await this.prepareSessionCustom()
                } else {
                    await this.prepareSessionPreset()
                }
            },
            async prepareSessionCustom() {
                // Custom session preparation
                let response = await apiGetSessionOptions(this.mode)
                this.sessionOptionsAll = response
                this.inputMarketsLen = this.sessionOptionsAll.markets.length
            },
            async prepareSessionPreset() {
                // Preseted (not custom) session preparation
                // Add userid and mode to object
                this.currentSession["options"]["values"] = {"userId": this.user.id, "mode": this.mode}
                this.prepareDecisions()
            },
            dateDisabled(ymd, date) {
                // Disable weekends in date input
                const weekday = date.getDay()
                // Return `true` if the date should be disabled
                return weekday == 0 || weekday == 6
                },
            updateInputTickers() {
                // If market dropdown value changed then filter securities dropdown with market value
                let inputMarket = this.$children.find(child => { return child.name === "input-market"; });
                let inputTicker = this.$children.find(child => { return child.name === "input-ticker"; });
                if (inputMarket.selected.code) {
                    // Clean selected value in securities dropdown
                    inputTicker.searchFilter = ""
                    // Get value from markets dropdown
                    this.selectedMarket = inputMarket.selected.code
                    // Set securities dropdown list length
                    this.inputTickersLen = inputMarket.selected.name ? this.sessionOptionsAll.tickers[this.selectedMarket].length : 0
                    // Add options in securities dropdown
                    this.sessionOptionsTickers = this.sessionOptionsAll.tickers[this.selectedMarket]
                }
            },
            async checkForm(e) {
                // Get selected session options and send it via API
                e.preventDefault()
                
                // Clean list of validation errors
                this.formErrors = []

                // Add userid and mode to object
                this.currentSession["options"]["values"] = {"userId": this.user.id, "mode": this.mode}

                // Get values from form and validate them (forEach context = this)
                this.$children.forEach(function(item) {
                    // Make checks only for inputs
                    if (item.name == undefined) {
                        return false
                    }

                    if (!item.name.includes("input-")) {
                        return false
                    }
                    // Check datepicker and vue-simple-search-dropdowns
                    let optionName = item.name.replaceAll("input-", "")
                    if (item.id == "input-date") {
                        if (item.formattedValue == "No date selected") {
                            this.formErrors.push(item.id)
                        } else {
                            this.currentSession["options"]["values"][optionName] = item.activeYMD
                        }
                    } else {
                        if (item.selected.id == undefined) {
                            this.formErrors.push(item.name)
                        } else {
                            
                            this.currentSession["options"]["values"][optionName] = item.selected.code
                        }
                    }
                }, this)
                
                // Go to Decision page
                if (this.formErrors.length == 0) {
                    await this.prepareDecisions()
                    this.goToDecisions()
                }
            },
            async prepareDecisions() {
                // Send POST request and save response to vuex state
                // If form validation has passed send POST request, check the response and go to the Decision page
                
                // Wait for async methods
                let response = await apiPostStartNewSession(this.currentSession["options"]["values"])
                // Add attributes from response to the object
                this.currentSession["options"]["values"]["sessionId"] = response.values["SessionId"]
                this.currentSession["options"]["values"]["timelimit"] = response.values["Timelimit"]
                this.currentSession["options"]["values"]["iterations"] = response.values["Iterations"]
                this.currentSession["options"]["values"]["barsnumber"] = response.values["Barsnumber"]
                this.currentSession["options"]["values"]["fixingbar"] = response.values["Fixingbar"]
                this.currentSession["options"]["values"]["slippage"] = response.values["Slippage"]

                this.currentSession["options"]["aliases"] = {
                    "market": response.aliases["Market"],
                    "ticker": response.aliases["Ticker"],
                    "timeframe": response.aliases["Timeframe"],
                    "barsnumber": response.aliases["Barsnumber"],
                    "timelimit": response.aliases["Timelimit"],
                    "date": response.aliases["Date"],
                    "iterations": response.aliases["Iterations"],
                    "slippage": response.aliases["Slippage"],
                    "fixingbar": response.aliases["Fixingbar"]
                }
                // Create first iteration in the current session (counter and storage)
                this.currentSession["currentIterationNum"] = 1
                this.currentSession["iterations"] = {1: {}}
            },
            goToDecisions() {
                // Go to the decision making page
                this.$router.push(`/decision/${this.currentSession["options"]["values"]["sessionId"]}/1`)
            },
            checkClassIsInputInvalid(element) {
                // Change class of dropdown if validation has failed
                let hasError = false
                if (this.formErrors.length > 0) {
                    hasError = this.formErrors.indexOf(element) >= 0 ? true : false
                }
                return {"is-input-invalid": hasError}
            }
        }
    }

</script>

<style scoped>

    label {
        display: flex;
        justify-content: center;
    }

    .form-control {
        font-size: 14px !important;
        height: 37px !important;
        display: flex !important;
        align-items: center !important;
    }

    #page-timer {
        position: absolute;
        width: 100%;
        height: calc(100% - 89px - 5px - 40px);
        top: 89px;
        font-size: 24px;
        font-weight: 700;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background-color: rgba(255,255,255,0.7);
        z-index: 1;
        text-align: center;
    }

    #page-timer-countdown {
        font-size: 14px;
        font-weight: 500;
    }

</style>