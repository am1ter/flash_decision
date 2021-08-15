<template>
    <section id='page'>
        <form @submit="checkForm">
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
                            :options="sessionOptions.markets"
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
                            :options="sessionOptions.timeframes"
                            placeholder="Select a timeframe">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Bars number</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="barsNumber"
                            :class="checkClassIsInputInvalid('barsNumber')"
                            :options="sessionOptions.barsNumber"
                            placeholder="Select a number of bars">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Time limit, sec.</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="timeLimit"
                            :class="checkClassIsInputInvalid('timeLimit')"
                            :options="sessionOptions.timeLimit"
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
                            :options="sessionOptions.iterations"
                            placeholder="Select a number of iterations">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Slippage, %</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="slippage"
                            :class="checkClassIsInputInvalid('slippage')"
                            :options="sessionOptions.slippage"
                            placeholder="Select a slippage level">
                        </Dropdown>
                    </b-col>
                    
                    <div class="w-100 my-1"></div>
                    
                    <b-col class="my-auto" sm="4">
                        <label>Fixing bar</label>
                    </b-col>
                    <b-col class="my-auto" sm="8">
                        <Dropdown 
                            name="fixingBar"
                            :class="checkClassIsInputInvalid('fixingBar')"
                            :options="sessionOptions.fixingBar"
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
    import { fetchSessionOptions } from '@/api'
    export default {
        name: 'page_Session',
        data() {
            return {
                sessionOptions: [],
                sessionOptionsSecurities: [],
                sessionOptionsMarketsLen: 10,
                sessionOptionsSecuritiesLen: 10,
                selectedMarket: 'Market.SHARES',
                currentSessionParams: [],
                dateMax: new Date(),
                dateMin: new Date(2019, 0, 1),
                formErrors: []
                }
        },
        computed: {
            ...mapState(['isAuth', 'user'])
        },
        methods: {
            dateDisabled(ymd, date) {
                // Disable weekends
                const weekday = date.getDay()
                // Return `true` if the date should be disabled
                return weekday == 0 || weekday == 6
                },
            getOptionsSecurities() {
                if (this.$children[1] != null) {
                    // Get value from markets dropdown
                    this.selectedMarket = 'Market.' + this.$children[0].selected.name
                    // Clean selected value in securities dropdown
                    this.$children[1].searchFilter = ''
                    // Set securities dropdown list length
                    this.sessionOptionsSecuritiesLen = this.$children[0].selected.name != '' ? this.sessionOptions.securities[this.selectedMarket].length : 0
                    // Add options in securities dropdown
                    this.sessionOptionsSecurities = this.sessionOptions.securities[this.selectedMarket]
                }
            },
            checkForm(e) {
                // Get selected session options and send it via API
                // Clean list of validation errors
                this.formErrors = []
                // Add userid to object
                this.currentSessionParams['userId'] = this.user.id
                // Get values from form and validate them
                for (let i = 0; i <= 8; i++) {
                    // Check datepicker
                    if (this.$children[i].id == "date") {
                        if (this.$children[i].formattedValue == "No date selected") {
                            this.formErrors.push(this.$children[i].id)
                        } else {
                            this.currentSessionParams[this.$children[i].id] = this.$children[i].activeYMD
                        }
                    } else {
                        if (this.$children[i].searchFilter == '') {
                            this.formErrors.push(this.$children[i].name)
                        } else {
                            this.currentSessionParams[this.$children[i].name] = this.$children[i].searchFilter
                        }
                    }
                }
                console.log(this.currentSessionParams)
                // If validation hasn't been passed than preventDefault form submit
                return this.formErrors.length == 0 ? true : e.preventDefault()
            },
            checkClassIsInputInvalid(element) {
                let hasError = false
                if (this.formErrors.length > 0) {
                    hasError = this.formErrors.indexOf(element) >= 0 ? true : false
                }
                return {isInputInvalid: hasError}
            }
        },
        beforeMount() {
            fetchSessionOptions()
                .then(response => {this.sessionOptions = response.data})
                .then(() => {this.sessionOptionsMarketsLen = this.sessionOptions.markets.length})
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    #page {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 15px 25px;
        width: auto;
    }

    label {
        display: flex;
        justify-content: center;
    }

    .isInputInvalid {
        border: 1px solid #dc3545;
        border-radius: 3px;
        padding-right: calc(1.5em + .75rem)!important;
        background-image: url('../assets/icons/i_formvalidation_error.svg')!important;
        background-position: right calc(.375em + .1875rem) center;
        background-repeat: no-repeat;
        background-size: calc(.75em + .375rem) calc(.75em + .375rem);
    }

</style>
