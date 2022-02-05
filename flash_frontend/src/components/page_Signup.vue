<template>
    <section id='page'>
        <div id='errors' v-if="apiErrors.length > 0">
            <p>{{apiErrors[0]}}</p>
        </div>
        <form v-if="apiErrors.length == 0 & isLoaded" @submit.prevent="checkForm" autocomplete="off">
            <b-container class="g-0" fluid>
                <b-row cols="2">
                    <b-col class="my-auto text-center" sm="3">
                        <label>Email*</label>
                    </b-col>
                    <b-col class="my-auto" sm="9">
                        <b-form-input id="input-email" :class="checkClassIsInputInvalid('input-email')"  placeholder="Enter your email"/>
                    </b-col>
                    <!-- Place for error messages (hidden if no errors) -->
                    <b-col class="my-auto" sm="3" v-if="formErrors.indexOf('input-email') > -1">
                        <!-- Empty cell -->
                    </b-col>                    
                    <b-col class="my-auto" sm="9" v-if="formErrors.indexOf('input-email') > -1">
                        <p class="text-danger text-left mb-0">
                            <small>Please enter a valid email</small>
                        </p>
                        <p class="text-danger text-left mb-0" v-if="emailIsFree == false">
                            <small>Email has already been taken</small>
                        </p>
                    </b-col>
                    <div class="w-100 my-1"></div>
                    <b-col class="my-auto text-center" sm="3">
                        <label>Name*</label>
                    </b-col>
                    <b-col class="my-auto" sm="9">
                        <b-form-input id="input-name" :class="checkClassIsInputInvalid('input-name')" placeholder="Enter your name"/>
                    </b-col>
                    <!-- Place for error messages (hidden if no errors) -->
                    <b-col class="my-auto" sm="3" v-if="formErrors.indexOf('input-name') > -1">
                        <!-- Empty cell -->
                    </b-col>                    
                    <b-col class="my-auto" sm="9" v-if="formErrors.indexOf('input-name') > -1">
                        <p class="text-danger text-left mb-0">
                            <small>Please enter your name</small>
                        </p>
                    </b-col>
                    <div class="w-100 my-1"></div>
                    <b-col class="my-auto text-center" sm="3">
                        <label>Password*</label>
                    </b-col>
                    <b-col class="my-auto" sm="9">
                        <b-form-input type='password' id="input-password" :class="checkClassIsInputInvalid('input-password')" placeholder="Enter your password"/>
                    </b-col>
                    <!-- Place for error messages (hidden if no errors) -->
                    <b-col class="my-auto" sm="3" v-if="formErrors.indexOf('input-password') > -1">
                        <!-- Empty cell -->
                    </b-col>                    
                    <b-col class="my-auto" sm="9" v-if="formErrors.indexOf('input-password') > -1">
                        <p class="text-danger text-left mb-0">
                            <small>Password must contain at least 6 symbols</small>
                        </p>
                    </b-col>
                </b-row>
            </b-container>
            <b-button type="submit" class="col-12 mt-3 gradient">Sign up</b-button>
            <b-button v-on:click="goToSignIn()" variant="outline-secondary" class="col-12 my-2">Back</b-button>
        </form>
    </section>
</template>

<script>
    import { mapState, mapMutations } from 'vuex'
    import { postCreateUser, checkEmailIsFree } from '@/api'

    export default {
        name: 'page_Signup',
        data() {
            return {
                isLoaded: true,
                formErrors: [],
                emailIsFree: true
                }
        },
        computed: {
            ...mapState(['isAuth', 'user', 'registrationForm', 'apiErrors'])
        },
        methods: {
            ...mapMutations(['setAuth', 'setUser']),
            async checkForm(e) {
            // Get data from inputs and send it via API
            
            // Clean list of validation errors
            this.formErrors = []

            // Check if email is free
            this.emailIsFree = await checkEmailIsFree(this.$children[0].localValue)

            // Get values from form and validate them
            for (let i = 0; i <= 2; i++) {
                // Check email (contains @), name (length) and password (length)
                let input_id = this.$children[i].id
                let input_value = this.$children[i].localValue
               
                if ((input_id == "input-email" & input_value.indexOf('@') > -1 & this.emailIsFree) ||
                    (input_id == "input-name" & input_value.length >= 2) ||
                    (input_id == "input-password" & input_value.length >= 6)) {
                        this.registrationForm[input_id.replace('input-', '')] = input_value
                } else {
                    this.formErrors.push(input_id)
                }
            }

            // Send POST request and save response to vuex state
            // If validation has failed (formErrors.length > 0) than decline form submit (preventDefault)
            // If validation has passed send POST request, check the response and go to the next page
            if (this.formErrors.length == 0) {
                let user = await postCreateUser(this.registrationForm)
                if (user) {
                    this.$store.commit('setUser', user)
                    this.$store.commit('setAuth', true)
                }
                // Go to the main page
                this.$router.push('/session/')
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
            },
            goToSignIn() {
                // Go to the login page
                this.$router.push('/sign-in/')
            }
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
</style>
