<template>
    <section id='page'>
        <b-container class="g-0 text-center" fluid>
            <b-row cols="2">
                <b-col class="my-auto" sm="4">
                    <label>Market</label>
                </b-col>
                <b-col class="my-auto" sm="8">
                     <Dropdown 
                        name="markets"
                        :options="sessionOptions.fixing_bar"
                        placeholder="Select a securities market">
                    </Dropdown>
                    <!-- <Dropdown 
                        :disabled="false"
                        :maxItem="10"
                        v-on:selected="validateSelection"
                        v-on:filter="getDropdownValues">
                    </Dropdown> -->
                </b-col>

                <div class="w-100 my-1"></div>

                <b-col class="my-auto" sm="4">
                    <label>Ticker</label>
                </b-col>
                <b-col class="my-auto" sm="8">
                    <Dropdown 
                        name="ticker"
                        :options="[{ id: 1, name: 'AFLT'}, { id: 2, name: 'AMD'}]"
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
                        :options="[{ id: 1, name: '5'}, { id: 2, name: '10'}]"
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
                        :options="[{ id: 1, name: '5'}, { id: 2, name: '10'}]"
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
                        :options="[{ id: 1, name: '5'}, { id: 2, name: '10'}]"
                        placeholder="Select a session time limit">
                    </Dropdown>
                </b-col>
                
                <div class="w-100 my-1"></div>
                
                <b-col class="my-auto" sm="4">
                    <label>Date</label>
                </b-col>
                <b-col class="my-auto" sm="8">
                    <Dropdown 
                        name="date"
                        :options="[{ id: 1, name: '5'}, { id: 2, name: '10'}]"
                        placeholder="Select start date">
                    </Dropdown>
                </b-col>
                
                <div class="w-100 my-1"></div>
                
                <b-col class="my-auto" sm="4">
                    <label>Iterations</label>
                </b-col>
                <b-col class="my-auto" sm="8">
                    <Dropdown 
                        name="iterations"
                        :options="[{ id: 1, name: '5'}, { id: 2, name: '10'}]"
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
                        :options="[{ id: 1, name: '5'}, { id: 2, name: '10'}]"
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
                        :options="[{ id: 1, name: '5'}, { id: 2, name: '10'}]"
                        placeholder="Select a result fixing bar">
                    </Dropdown>
                </b-col>
            </b-row>
        </b-container>
        <b-button class="col-12 mt-3 gradient rounded-1">Start</b-button>
    </section>
</template>

<script>
    import { fetchSessionOptions } from '@/api'
    export default {
        name: 'page_Session',
        data() {
            return {
                sessionOptions: "[{ id: 1, name: '5'}, { id: 2, name: '10'}]"
                }
        },
        beforeMount() {
            fetchSessionOptions().then(response => {
                this.sessionOptions = response.data
                })
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

</style>
