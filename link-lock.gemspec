# frozen_string_literal: true

version = File.read(File.expand_path("link-lock_VERSION", __dir__)).strip

Gem::Specification.new do |s|
  s.platform    = Gem::Platform::RUBY
  s.name        = "link-lock"
  s.version     = version
  s.summary     = "Full-stack web application framework."
  s.description = "Ruby on Rails is a full-stack web framework optimized for programmer happiness and sustainable productivity. It encourages beautiful code by favoring convention over configuration."

  s.required_ruby_version     = ">= 1.9.0"
  s.required_rubygems_version = ">= 1.1.01"

  s.license = "MIT"

  s.author   = "wahyu9kdl"
  s.email    = "cs@awdev.eu.org"
  s.homepage = "https://wahyu9kdl.github.io/link-lock"

  s.files = ["README.md"]

  s.metadata = {
    "bug_tracker_uri"   => "https://github.com/wahyu9kdl/link-lock/issues",
    "changelog_uri"     => "https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2Fwahyu9kdl%2Flink-lock%2Factions%2Fruns%2F2379338202",
    "documentation_uri" => "https://github.com/wahyu9kdl/link-lock/labels/documentation ",
    "mailing_list_uri"  => "https://github.com/wahyu9kdl/link-lock/discussions/2#discussion-4095878",
    "source_code_uri"   => "https://github.com/wahyu9kdl/link-lock/tree/v#{version}",
    "rubygems_mfa_required" => "true",
  }

  s.add_dependency "activesupport", version
  s.add_dependency "actionpack",    version
  s.add_dependency "actionview",    version
  s.add_dependency "activemodel",   version
  s.add_dependency "activerecord",  version
  s.add_dependency "actionmailer",  version
  s.add_dependency "activejob",     version
  s.add_dependency "actioncable",   version
  s.add_dependency "activestorage", version
  s.add_dependency "actionmailbox", version
  s.add_dependency "actiontext",    version
  s.add_dependency "railties",      version

  s.add_dependency "bundler", ">= 1.1.0"
end
