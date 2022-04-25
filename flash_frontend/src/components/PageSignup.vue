<template>
    <section id="page" v-if="apiErrors.length == 0 & isLoaded" >
        <form @submit.prevent="checkForm">
            <b-container class="g-0" fluid>
                <b-row cols="2">
                    <b-col class="my-auto text-center col-3">
                        <label>Email*</label>
                    </b-col>
                    <b-col class="my-auto col-9">
                        <b-form-input id="input-email" :class="checkClassIsInputInvalid('input-email')"  placeholder="Enter your email"/>
                    </b-col>
                    <!-- Place for error messages (hidden if no errors) -->
                    <b-col class="my-auto col-3" v-if="formErrors.indexOf('input-email') > -1">
                        <!-- Empty cell -->
                    </b-col>                    
                    <b-col class="my-auto col-9" v-if="formErrors.indexOf('input-email') > -1">
                        <p class="text-danger text-left mb-0" v-if="emailIsFree == true">
                            <small>Please enter a valid email</small>
                        </p>
                        <p class="text-danger text-left mb-0" v-if="emailIsFree == false">
                            <small>Email has already been taken</small>
                        </p>
                    </b-col>
                    <div class="w-100 my-1"></div>
                    <b-col class="my-auto text-center col-3">
                        <label>Name*</label>
                    </b-col>
                    <b-col class="my-auto col-9">
                        <b-form-input id="input-name" :class="checkClassIsInputInvalid('input-name')" placeholder="Enter your name"/>
                    </b-col>
                    <!-- Place for error messages (hidden if no errors) -->
                    <b-col class="my-auto col-3" v-if="formErrors.indexOf('input-name') > -1">
                        <!-- Empty cell -->
                    </b-col>                    
                    <b-col class="my-auto col-9" v-if="formErrors.indexOf('input-name') > -1">
                        <p class="text-danger text-left mb-0">
                            <small>Please enter your name</small>
                        </p>
                    </b-col>
                    <div class="w-100 my-1"></div>
                    <b-col class="my-auto text-center col-3">
                        <label>Password*</label>
                    </b-col>
                    <b-col class="my-auto col-9">
                        <b-form-input type="password" id="input-password" :class="checkClassIsInputInvalid('input-password')" placeholder="Enter your password"/>
                    </b-col>
                    <!-- Place for error messages (hidden if no errors) -->
                    <b-col class="my-auto col-3" v-if="formErrors.indexOf('input-password') > -1">
                        <!-- Empty cell -->
                    </b-col>                    
                    <b-col class="my-auto col-9" v-if="formErrors.indexOf('input-password') > -1">
                        <p class="text-danger text-left mb-0">
                            <small>Password must contain at least 6 symbols</small>
                        </p>
                    </b-col>
                </b-row>
                <p id="usage-terms" class="text-center mx-1">
                    By signing up, you agree with Terms of Services and Privacy Policy
                </p>
            </b-container>
            <b-button id="button-signup" type="submit" squared class="col-12 mt-3 gradient">Sign up</b-button>
            <b-button id="button-go-back" v-on:click="goToSignIn()" squared variant="outline-secondary" class="col-12 my-2">Back</b-button>
        </form>
    </section>
</template>

<script>
    import { mapState, mapMutations } from "vuex"
    import { apiPostCreateUser, apiGetCheckEmailIsFree } from "@/api"

    export default {
        name: "PageSignup",
        data() {
            return {
                isLoaded: true,
                formErrors: [],
                registrationForm: {},
                emailIsFree: true
                }
        },
        computed: {
            ...mapState(["user", "apiErrors"])
        },
        methods: {
            ...mapMutations(["setUserFromApi"]),
            async checkForm(e) {
                // Get data from inputs and send it via API
                e.preventDefault()

                // Check if email is free
                this.emailIsFree = await apiGetCheckEmailIsFree(this.$children[0].localValue)

                // Clean list of validation errors
                this.formErrors = []
                this.registrationForm = {}

                // Get values from form and validate them
                for (let i = 0; i <= 2; i++) {
                    // Check email (contains @), name (length) and password (length)
                    let input_id = this.$children[i].id
                    let input_value = this.$children[i].localValue

                    if (input_id == "input-email" && input_value.indexOf("@") > -1 && input_value.indexOf(".") > -1 && this.emailIsFree) {
                        this.registrationForm[input_id.replace("input-", "")] = input_value
                    } else if (input_id == "input-name" && input_value.length >= 2) {
                        this.registrationForm[input_id.replace("input-", "")] = input_value
                    } else if (input_id == "input-password" && input_value.length >= 6) {
                        this.registrationForm[input_id.replace("input-", "")] = input_value
                    } else {
                        this.formErrors.push(input_id)
                    }
                }

                // If form validation has failed then stop
                if (this.formErrors.length > 0) {
                    return false 
                }

                // If validation has passed send POST request, save response to vuex state and go to the next page
                let user = await apiPostCreateUser(this.registrationForm)
                if (user) {
                    this.$store.commit("setUserFromApi", user)
                }

                // Go to the main page
                this.$router.push("/session/custom/")
            },
            checkClassIsInputInvalid(element) {
                // Change class of dropdown if validation has failed
                let hasError = false
                if (this.formErrors.length > 0) {
                    hasError = this.formErrors.indexOf(element) >= 0 ? true : false
                }
                return {"is-input-invalid": hasError}
            },
            goToSignIn() {
                // Go to the login page
                this.$router.push("/login/")
            }
        }
    }
</script>

<style scoped>

    #page {
        height: calc(100vh - 54px - 105px - 34px - 80px);
    }

    #usage-terms {
        font-size: 0.80em;
        font-weight: 400;
        color: #6c757d;
        margin: 15px 5px 0px 5px;
    }

</style>