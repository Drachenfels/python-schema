# Changelog

---
## Planned

Remaining missing elements of project in no particular order:

 * add a way to mark certain fields as required + validation
 * add test-coverage
 * make it possible to self-reference for schema and collections when
   performing loads (when object provides UUID, use it as identity check)
 * make sure that defaults on SchemaField do work
 * context manager to inject error message into SchemaField, ie. we check with
   db for uniquness of user name and if it's not unique, then we mark
   UserSchema as having error on username with message 'Username has to be
   unique'
 * support error codes, from github: 'When validation/parsing error is
   generated under certain conditions it should be possible to generate stable
   list of error codes for programmatic error handling'
 * implement context, when performing dumps and/or loads we can mangle data to
   take into account for example user and his/her timezone
 * make sure that class kwargs are passed when we create instance of collection
   and/or schema schema, right now we call make_new without actually passing
   any kwargs or in some cases only some of them
 * allow to use default value when loaded payload is None and we disallow None
   values
 * make sure that default value is working as expected, especially on schema
   class, where we load with incomplete dictionary
 * allow loads without arugments (default values will kick in), also make sure
   that schema that contains other schema if we load without arugments
   subschema will use default values (watch out for recursion)

---
## Release 0.4

### Core

 * SchemaField that can be build using other fields as a defintion
 * lazy loading of other classes for cases when SchemaField is using itself as a definition
 * CollectionField was upgraded to allow lazy load as well

---
## Release 0.3

### Core

 * add StrField
 * add CollectionField

---
## Release 0.2

### Core

 * add IntField

---
## Release 0.1

### Core

 * add BaseField
 * allow basic validation of given fields
