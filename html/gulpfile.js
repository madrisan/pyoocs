var gulp        = require('gulp'),
    minifycss   = require('gulp-minify-css'),
    jshint      = require('gulp-jshint'),
    stylish     = require('jshint-stylish'),
    uglify      = require('gulp-uglify'),
    usemin      = require('gulp-usemin'),
    imagemin    = require('gulp-imagemin'),
    rename      = require('gulp-rename'),
    concat      = require('gulp-concat'),
    notify      = require('gulp-notify'),
    cache       = require('gulp-cache'),
    changed     = require('gulp-changed'),
    rev         = require('gulp-rev'),
    browserSync = require('browser-sync'),
    ngannotate  = require('gulp-ng-annotate'),
    del         = require('del'),
    less        = require('gulp-less'),
    gutil       = require('gulp-util'),
    replace     = require('gulp-replace');

gutil.log('Reading the json configuration file',
          gutil.colors.cyan('\'oocs-cfg.json\'') + '...');
var oocs_cfg = require('../oocs-cfg.json');
gutil.log(' - baseUrl: \'' +
          gutil.colors.cyan(oocs_cfg['oocs-html-opts'].baseUrl) + '\'');

var cfg = {
    dist: 'server/public/',
    baseURL: oocs_cfg['oocs-html-opts'].baseUrl
};

// JavaScript syntax checker
gulp.task('jshint', function() {
    return gulp.src('app/scripts/**/*.js')
            .pipe(jshint())
            .pipe(jshint.reporter(stylish));
});

// Clean
gulp.task('clean', function() {
    return del([cfg.dist]);
});

// Default task
gulp.task('default', ['clean'], function() {
    gulp.start('buildless', 'usemin', 'copyviews', 'imagemin', 'copyfonts');
});

// Minification and uglification
gulp.task('usemin', ['buildless', 'jshint'], function () {
    return gulp.src('./app/index.html')
            .pipe(usemin({
                css: [minifycss(), rev()],
                js: [replace('@baseURL@', cfg.baseURL),
                     ngannotate(), uglify(), rev()]
            }))
            .pipe(gulp.dest(cfg.dist));
});

// Views
gulp.task('copyviews', function() {
    return gulp.src('app/views/**/*.html')
            .pipe(gulp.dest(cfg.dist + '/views/'));
});

// Images
gulp.task('imagemin', function() {
    return del([cfg.dist + '/images/']), gulp.src('app/images/**/*')
            .pipe(cache(imagemin({
                optimizationLevel: 3,
                progressive: true,
                interlaced: true
            })))
            .pipe(gulp.dest(cfg.dist + '/images/'))
            .pipe(notify({ message: 'Images task complete' }));
});

// Fonts
gulp.task('copyfonts', function() {
    gulp.src('./bower_components/font-awesome/fonts/**/*.{ttf,woff,eof,svg}*')
     .pipe(gulp.dest(cfg.dist + '/fonts/'));

    gulp.src('./bower_components/bootstrap/dist/fonts/**/*.{ttf,woff,eof,svg}*')
     .pipe(gulp.dest(cfg.dist + '/fonts/'));
});

// CSS
gulp.task('buildless', function() {
    return gulp.src('app/styles/**/*.less')
     .pipe(less())
     .pipe(gulp.dest('./app/styles'));
});

// Watch
gulp.task('watch', ['browser-sync'], function() {
  // Watch .js .css and .html files
  gulp.watch('{app/scripts/**/*.js,app/styles/**/*.less,app/**/*.html}', ['usemin']);

  // Watch views html files
  gulp.watch('app/views/**/*.html', ['copyviews']);

  // Watch image files
  gulp.watch('app/images/**/*', ['imagemin']);

});

gulp.task('browser-sync', ['default'], function () {
    var files = [
        'app/index.html',
        'app/views/**/*.html',
        'app/styles/**/*.css',
        'app/images/**/*.png',
        'app/scripts/**/*.js',
        cfg.dist + '/**/*'
    ];

    browserSync.init(files, {
        server: {
            baseDir: cfg.dist,
            index: "index.html"
        }
    });

    // Watch any files in dist/, reload on change
    gulp.watch([cfg.dist + '/**']).on('change', browserSync.reload);
});
