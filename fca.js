
class Concept{
    constructor(intent, bit){
	this.subconcepts = [];
	this.extent = [];
	if (!bit) this.intent = new BinaryVector(intent);
	else this.intent = intent;
    }
    equivalent(c) {return this.intent.equals(c.intent);}
    intersection(c) {return new Concept(this.intent.intersection(c.intent), true);}
    createLabels(attr, obj){
	this.attributes = [];	
	for(var i in attr) if (this.intent.get(i)) this.attributes.push(attr[i]);
	this.objects = []
	for(var i in obj) if (this.extent.get(i)) this.objects.push(obj[i]);
    }
    subsumes(c) {return this.intersection(c).equivalent(this);}
    addSubConcept(c){
	var found = false;
	var toRemove = [];
	for(var sc in this.subconcepts){
	    var scc = this.subconcepts[sc];
	    if (scc.subsumes(c)) {found = true; break;}
	    if (c.subsumes(scc)) toRemove.push(sc);
	}
	if (!found) this.subconcepts.push(c);
	for (var tr in toRemove) this.subconcepts.splice(toRemove[tr], 1);
    }
}

class FormalContext{    
    constructor(attributes, objects, matrix){
	this.attributes = attributes;
	this.objects = objects;
	this.matrix = matrix;
	this.concepts = []		
    }
    // super basic algorithm to build
    // concepts (only intent)
    buildConcepts(){
	for(var i in this.matrix){
	    var c = new Concept(matrix[i], false);
	    this.addConcept(c);
	}
    }
    // basic function used for incremental
    // building of lattice
    addConcept(c){
	if (!this.conceptExist(c)) {
	   var toAdd = []
	    for (var oc in this.concepts){
		var nc = this.concepts[oc].intersection(c);
		if (!this.conceptExist(nc)) {
		    var found = false;
		    for (var cc in toAdd){
			if (toAdd[cc].equivalent(nc)) found = true;
		    }
		    if (!found) toAdd.push(nc);
		}
	    }
	    for (var oc in toAdd){
		this.concepts.push(toAdd[oc]);
	    }
	    if (!this.conceptExist(c)) {
		this.concepts.push(c);
	    }
	}
    }
    conceptExist(c){
	for (var i in this.concepts){
	    if (this.concepts[i].equivalent(c)) return true;
	}
	return false;
    }
    buildTaxonomy(){
	for(var c1 in this.concepts){
	    for(var c2 in this.concepts){
		if (c1!=c2){
		    var cc1 = this.concepts[c1];
		    var cc2 = this.concepts[c2];		    
		    if (cc1.subsumes(cc2) && !cc2.subsumes(cc1)) cc1.addSubConcept(cc2);
		    else if (cc2.subsumes(cc1)) cc2.addSubConcept(cc1);
		}
	    }
	}
	this.addParents();
    }
    addParents(){
	for(var c1 in this.concepts){
	    this.concepts[c1].superconcepts = [];
	    for (var c2 in this.concepts)
		if (this.concepts[c2].subconcepts.includes(this.concepts[c1])) this.concepts[c1].superconcepts.push(this.concepts[c2]);
	}
    }
    addLabels(){
	for (var c in this.concepts){
	    this.concepts[c].createLabels(this.attributes, this.objects);
	}
    }
    root(){
	if (this.concepts.length == 0) return undefined;
	if (this._root) return this._root;
	var max = this.concepts[0];
	for (var c in this.concepts){
	    if (this.concepts[c].subsumes(max)) max = this.concepts[c];
	}
	this._root = max;
	return max;
    }
    populate(){
	for (var c in this.concepts){
	    var bv = [];	    
	    for(var i in this.matrix) {
		var ci = new Concept(this.matrix[i], false);
		if (this.concepts[c].subsumes(ci)) bv.push(true);
		else bv.push(false);
	    }
	    this.concepts[c].extent = new BinaryVector(bv);
	}
    }
}

