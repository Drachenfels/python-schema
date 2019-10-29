# Changelog

---
## Planned

 * replace \*args, \*\*kwargs on child classes (like SchemaField) with properly
   named arguments (if there is not too many of them)
 * add coverage
 * make it possible to self-reference for schema and collections when
   performing loads (when object provides UUID, use it as identity check)
 * make sure that CollectionField might be lazy loaded as well and in general
   behaves similar to SchemaField on that front


---
## Release 0.4

### Core

 * SchemaField that can be build using other fields as a defintion
 * lazy loading of other classes for cases when SchemaField is using itself as a definition
 * CollectionField was upgraded to allow lazy load as well

 - test case for SchemaField with two parents that override each other's attributes
 - test case for CollectionField with SchemaField in it
 - if we disallow Nones and Nones comes and we have default, should we or should not use that default? (tend to think we should use default but only if another flag attribute default-when-none is set to True (default is False), otherwise default is only in use when we perform explicit loads without arguments)
 - default values for SchemaField
 - test case for SchemaField using CollectionField with SchemaFields
 - test case for SchemaField inside of SchemaField (user with many addresses)
 - allow to perform loads without arguments (it will make default truly usable)
 - test case for using default values (for simple and complex fields)
 - when dealing with defauls, make sure no recurssion will happen when we have schema of each other and both have some sane defaults
 - there is no fields on schema, there is either very good reason for that or we need to put it back, it's confusing when and how fields are defined, what should happen is that we validate that fields is not empty
 - there is no way to set description, validators or allow_none on schema as it is right now
 - possibly makes sense to put all the values like validators/default/etc to be part of own configuration

---
## Release 0.3

---
## Release 0.2

---
## Release 0.1
