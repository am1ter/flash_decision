<template>
    <section id='page'>
        <!-- Show error if there is any errors -->
        <div id='errors' v-if="apiErrors.length > 0">
            <p>{{apiErrors[0]}}</p>
        </div>
        <!-- Get session option via API, wait for user input and then submit it back to API -->
        <form v-if="apiErrors == 0" @submit.prevent="checkForm">
            <b-container class="g-0" fluid>
                <b-row cols="2">
                    <!-- Parameters -->
                    <b-col class="my-auto" sm="4">
                        <label>Market</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="market"
                            :class="checkClassIsInputInvalid('market')"
                            :options="sessionOptionsAll.markets"
                            :maxItem="sessionOptionsMarketsLen"
                            v-on:selected="getOptionsSecurities"
                            autocomplete="off"
                            placeholder="Select a securities market">
                        </Dropdown>
                        <!-- <Dropdown 
                            :disabled="false"
                            v-on:filter="validateSelection"
                        </Dropdown> -->
                    </b-col>

                    <div class="w-100 my-1"></div>

                    <b-col class="my-auto" sm="4">
                        <label>Ticker</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="ticker"
                            :class="checkClassIsInputInvalid('ticker')"
                            :options="sessionOptionsSecurities"
                            :maxItem="sessionOptionsSecuritiesLen"
                            placeholder="Select a security">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Timeframe</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown
                            name="timeframe"
                            :class="checkClassIsInputInvalid('timeframe')"
                            :options="sessionOptionsAll.timeframes"
                            placeholder="Select a timeframe">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Bars number</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="barsnumber"
                            :class="checkClassIsInputInvalid('barsnumber')"
                            :options="sessionOptionsAll.barsnumber"
                            placeholder="Select a number of bars">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Time limit</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="timelimit"
                            :class="checkClassIsInputInvalid('timelimit')"
                            :options="sessionOptionsAll.timelimit"
                            placeholder="Select a session time limit">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Date</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <b-form-datepicker 
                            id="date" 
                            size="sm"
                            placeholder="Select a start date"
                            :class="checkClassIsInputInvalid('date')"
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
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Iterations</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="iterations"
                            :class="checkClassIsInputInvalid('iterations')"
                            :options="sessionOptionsAll.iterations"
                            placeholder="Select a number of iterations">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Slippage</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="slippage"
                            :class="checkClassIsInputInvalid('slippage')"
                            :options="sessionOptionsAll.slippage"
                            placeholder="Select a slippage level">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Fixing bar</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="fixingbar"
                            :class="checkClassIsInputInvalid('fixingbar')"
                            :options="sessionOptionsAll.fixingbar"
                            placeholder="Select a result fixing bar">
                        </Dropdown>
                    </b-col>
                </b-row>
            </b-container>
            <!-- Start button -->
            <b-button type="submit" class="col-12 mt-3 gradient rounded-1">Start</b-button>
        </form>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    import { fetchSessionOptions, postStartNewSession } from '@/api'

    export default {
        name: 'page_Session',
        data() {
            return {
                sessionOptionsAll: [],
                sessionOptionsMarketsLen: 10,
                sessionOptionsSecurities: [],
                sessionOptionsSecuritiesLen: 10,
                selectedMarket: 'Market.SHARES',
                dateMax: new Date(),
                dateMin: new Date(2019, 0, 1),
                formErrors: [],
                apiErrors: []
                }
        },
        computed: {
            ...mapState(['isAuth', 'user', 'currentSession'])
        },
        methods: {
            dateDisabled(ymd, date) {
                // Disable weekends in date input

                const weekday = date.getDay()
                // Return `true` if the date should be disabled
                return weekday == 0 || weekday == 6
                },
            getOptionsSecurities() {
                // If market dropdown value changed then filter securities dropdown with market value
                if (this.$children[1]) {
                    // Condition alse used for prevent exec after loading

                    // Clean selected value in securities dropdown
                    this.$children[1].searchFilter = ''
                    // Get value from markets dropdown
                    this.selectedMarket = this.$children[0].selected.code
                    // Set securities dropdown list length
                    this.sessionOptionsSecuritiesLen = this.$children[0].selected.name ? this.sessionOptionsAll.securities[this.selectedMarket].length : 0
                    // Add options in securities dropdown
                    this.sessionOptionsSecurities = this.sessionOptionsAll.securities[this.selectedMarket]
                }
            },
            checkForm(e) {
                // Get selected session options and send it via API
                
                // Clean list of validation errors
                this.formErrors = []

                // Add userid to object
                this.currentSession['options'] = {'userId': this.user.id}

                // Get values from form and validate them
                for (let i = 0; i <= 8; i++) {
                    // Check datepicker and vue-simple-search-dropdowns
                    if (this.$children[i].id == "date") {
                        if (this.$children[i].formattedValue == "No date selected") {
                            this.formErrors.push(this.$children[i].id)
                        } else {
                            this.currentSession['options'][this.$children[i].id] = this.$children[i].activeYMD
                        }
                    } else {
                        if (this.$children[i].selected.length == 0) {
                            this.formErrors.push(this.$children[i].name)
                        } else {
                            this.currentSession['options'][this.$children[i].name] = this.$children[i].selected.code
                        }
                    }
                }

                // Send POST request and save response to vuex state
                // If validation has failed than decline form submit (preventDefault)
                if (this.formErrors.length == 0) {
                    postStartNewSession(this.currentSession['options'])
                        .then(
                            response => {
                                this.currentSession['options']['sessionId'] = response.data
                                this.$router.push('/decision')
                                },
                            reject => {this.apiErrors.push(reject)}
                            )
                } else {
                   e.preventDefault()
                }
            },
            checkClassIsInputInvalid(element) {
                // Change class of dropdown if validation has failed
                let hasError = false
                if (this.formErrors.length > 0) {
                    hasError = this.formErrors.indexOf(element) >= 0 ? true : false
                }
                return {isInputInvalid: hasError}
            }
        },
        beforeMount() {
            fetchSessionOptions()
                .then(
                    response => {this.sessionOptionsAll = response.data},
                    reject => {this.apiErrors.push(reject)}
                )
                .then(() => {this.sessionOptionsMarketsLen = this.sessionOptionsAll.markets.length})
        }
    }
</script>

<style scoped>
    #page {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 15px 25px;
        width: auto;
    }

    #errors {
        position: absolute;
        width: 100vw;
        height: 100vh;
        top: 0px;
        font-size: 24px;
        font-weight: 700;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: rgba(255,255,255,0.7);
    }

    label {
        display: flex;
        justify-content: center;
    }

    .isInputInvalid {
        border: 1px solid #dc3545;
        border-radius: 3px;
        font-size: 14px;
        padding-right: calc(1.5em + .75rem)!important;
        background-image: url('../assets/icons/i_formvalidation_error.svg') !important;
        background-position: right calc(.375em + .1875rem) center;
        background-repeat: no-repeat;
        background-size: calc(.75em + .375rem) calc(.75em + .375rem);
    }

</style>
