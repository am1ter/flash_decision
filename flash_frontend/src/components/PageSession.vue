<template>
    <section id="page">
        <!-- Get session option via API, wait for user input and then submit it back to API -->

        <!-- Mode selection menu -->
        <b-button-group class="w-100">
            <router-link id="button-classic" :to="{name: 'Session page', params: {'mode': 'classic'}}" tag="div" class="w-50 py-5 m-1 tile">
                <img src="../assets/icons/i_mode_classic.svg" alt="Icon">
                Classic
            </router-link>
            <router-link id="button-blitz" :to="{name: 'Session page', params: {'mode': 'blitz'}}" tag="div" class="w-50 py-5 m-1 tile">
                <img src="../assets/icons/i_mode_blitz.svg" alt="Icon">
                Blitz
            </router-link>
        </b-button-group>
        <b-button-group class="w-100">
            <router-link id="button-crypto" :to="{name: 'Session page', params: {'mode': 'crypto'}}" tag="div" class="w-50 py-5 m-1 tile">
                <img src="../assets/icons/i_mode_crypto.svg" alt="Icon">
                Crypto
            </router-link>
            <router-link id="button-custom" :to="{name: 'Session page', params: {'mode': 'custom'}}" tag="div" class="w-50 py-5 m-1 tile">
                <img src="../assets/icons/i_mode_custom.svg" alt="Icon">
                Custom
            </router-link>
        </b-button-group>

        <!-- Modes description -->
        <div class="mt-3">
            <h3 class="desc-header pb-1 mb-1">Modes description</h3>
            <h4 class="desc-subheader">Classic</h4>
            <p>Would you like to practice in trading of preset shares on USA market? Start a classic session right now.</p>
            <h4 class="desc-subheader">Blitz</h4>
            <p>Listen to your intuition and make fast decisions. You will get 10 chances and only 5 second for each decision.</p>
            <h4 class="desc-subheader">Crypto</h4>
            <p>High volatility, unpredictability, high returns - is that what you looking for? All this is related to cryptocurrencies.</p>
            <h4 class="desc-subheader">Custom</h4>
            <p>Choose from thousands securities and set up all other options manually for your own individual session.</p>
        </div>

    </section>
</template>

<script>
    import { mapState } from "vuex"
    
    export default {
        name: "PageSession",
        components: {
        },
        data() {
            return {}
        },
        computed: {
            ...mapState(["user", "currentSession"])
        },
        beforeMount() {},
        methods: {}
    }
</script>

<style scoped>

    p {
        font-size: 14px;
    }

    @media (max-width: 380px) {
        p {
            font-size: 13px;
        }
    }

    #session_mode {
        width: 100%;
    }

    .tile {
        background: #464646;
        display: flex;
        align-items: center;
        flex-direction: column;
        cursor: pointer;
        color: #FFFFFF;
    }
    
    .desc-header {
        font-size: 14px;
        font-weight: 500;
        color: #0B5A73;
        border-bottom: 1px solid #0B5A73;
        width: fit-content;
        margin: auto;
    }   

    .desc-subheader {
        text-align: left;
        font-size: 14px;
        font-weight: 500;
        color: #333333;
    }

    .light {
        background: #888888;
    }

    .tile:focus, .tile:hover {
        background: linear-gradient(to right, #280B3F, #0E4280, #076583);
    }

</style>