var mongoose = require('mongoose');

var scanSchema = {
    hostname: {
        type: String,
        required: true
    },
    distribution: Object,
    modules: Object,
    scan_time: {
        type: Date, default: Date.now
    },
    summary : {
        criticals: {
            type: Number, default: 0
        },
        infos: {
            type: Number, default: 0
        },
        max_severity: {
            type: String, required: true
        },
        warnings: {
            type: Number, default: 0
        }
    }
};

module.exports = new mongoose.Schema(scanSchema);
module.exports.scanSchema = scanSchema;
