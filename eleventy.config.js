module.exports = function (eleventyConfig) {
  eleventyConfig.addWatchTarget("docs/data");

  eleventyConfig.addPassthroughCopy({
    "site/assets": "assets"
  });

  return {
    dir: {
      input: "site",
      includes: "_includes",
      layouts: "_includes/layouts",
      data: "_data",
      output: "_site"
    },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};
