var mongoose = require('mongoose')
  , passportLocalMongoose = require('passport-local-mongoose');

var userSchema = {
    profile: {
        email: {
            type: String,
            required: true,
            lowercase: true,
            unique: true
        },
        password: {
            type: String,
            required: true
        },
    },
    admin: {
        type: Boolean, default: false
    }
};

var User = new mongoose.Schema(userSchema);

// Passport-Local Mongoose will add a username, hash and salt field to store
// the username, the hashed password and the salt value.
User.plugin(passportLocalMongoose);

module.exports = mongoose.model('User', User);
