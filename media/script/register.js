jQuery(function(){
    var elements = {
        fieldEmail: jQuery('#email'),
        fieldPhone: jQuery('#phone'),
        fieldFirstName: jQuery('#first_name'),
        fieldLastName: jQuery('#last_name'),
        fieldBirthdate: jQuery('#birthdate'),
        fieldCorporateEmail: jQuery('#corporate_email'),
        fieldCompany: jQuery('#company'),
        fieldDesignation: jQuery('#designation'),
        fieldsetPersonal: jQuery('#fieldset_personal'),
        fieldsetWorkProfile: jQuery('#fieldset_work_profile'),
        fieldsetMailingAddress: jQuery('#fieldset_mailing_address'),
        fieldsetContact: jQuery('#fieldset_contact')
    };
    var DISPLAY_SPEED = 'fast';

    AnyTime.picker('birthdate', {format:"%d-%m-%Y"});

    // Validations
    // Contact fieldset.
    var paramsFieldsetContact = {
        onValid: function(){
            this.insertMessage(this.createMessageSpan());
            this.addFieldClass();
            if (elements.fieldEmail.val()
                && elements.fieldPhone.val()){
                elements.fieldsetPersonal.show(DISPLAY_SPEED);
            }
        }
    };
    new LiveValidation('email', paramsFieldsetContact)
        .add(Validate.Presence)
        .add(Validate.Email);
    new LiveValidation('phone', paramsFieldsetContact)
        .add(Validate.Presence);

    // Personal fieldset.
    var paramsFieldsetPersonal = {
        onValid: function(){
            this.insertMessage(this.createMessageSpan());
            this.addFieldClass();
            if (elements.fieldFirstName.val()
                && elements.fieldLastName.val()
                && elements.fieldBirthdate.val()){
                elements.fieldsetWorkProfile.show(DISPLAY_SPEED);
            }
        }
    };
    new LiveValidation('first_name', paramsFieldsetPersonal).add(Validate.Presence);
    new LiveValidation('last_name', paramsFieldsetPersonal).add(Validate.Presence);
    new LiveValidation('birthdate', paramsFieldsetPersonal)
        .add(Validate.Presence)
        .add(Validate.Format, {pattern: /\d{2}-\d{2}\-\d{4}/i, failureMessage: 'The date format is not correct.'});

    // Work profile fieldset.
    var paramsFieldsetWorkProfile = {
        onValid: function(){
            this.insertMessage(this.createMessageSpan());
            this.addFieldClass();
            if (elements.fieldCompany.val()
                && elements.fieldDesignation.val()){
                elements.fieldsetMailingAddress.show(DISPLAY_SPEED);
            }
        }
    };
    new LiveValidation('corporate_email', paramsFieldsetWorkProfile).add(Validate.Email);
    new LiveValidation('company', paramsFieldsetWorkProfile).add(Validate.Presence);
    new LiveValidation('designation', paramsFieldsetWorkProfile).add(Validate.Presence);


});
