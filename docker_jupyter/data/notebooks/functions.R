## common functions
clear_pckg <- function(){
    options(warn=-1)
    lapply(paste('package:',names(sessionInfo()$otherPkgs),sep=""),detach,character.only=TRUE,unload=TRUE)
    options(warn=0)
}

add_func_annot <- function(df, annots, join_by = "feature"){
    if (is.character(annots)){
        annots <- read_tsv(annots, col_types = cols())
    }
    
    full_annot <- left_join(df, annots, by = setNames(join_by, "feature") ) 

    return(full_annot)
}

write_annot <- function(df, path){
    df <- sapply(df, as.character)
    df[is.na(df)] <- ""
    write.table(as.data.frame(df), path, quote=FALSE, 
            row.names=FALSE, sep="\t", na = "")
}

## for epic2 results
annotate_peaks <- function(gff, grMN){
    options(warn=-1)
    txdb <- makeTxDbFromGFF(file=gff, format="gff", dataSource="bra_3.0", organism="Brassica rapa")
    annoData <- toGRanges(txdb, feature="gene")

    peaks.anno <- annotatePeakInBatch(grMN, AnnotationData=annoData, 
                                  output="overlapping")
    peak_table <- as.data.frame(peaks.anno)
    
    options(warn=0)
    return(peak_table)
}

epic_annot <- function(bed_path, gff, annots){
    gr <- toGRanges(bed_path, format="broadPeak")
    peaks_anno_df <- annotate_peaks(gff, gr)
    epic_annot <- add_func_annot(peaks_anno_df, annots)
    
    return(epic_annot)
}

## for manorm
get_metadat <- function(bed, gr1){
    gr2 <- toGRanges(bed, format="broadPeak")
    ol <- findOverlaps(gr1, gr2)

    peaks <- cbind(as_tibble(ol), peaks = names(gr2)[as.matrix(ol)[,2]])
    peaks <- aggregate(peaks ~ queryHits, data = peaks, paste, collapse = ",")
    peaks <- left_join(tibble(queryHits = seq(nrow(values(gr1)))), peaks, by = "queryHits")
    
    FC <- cbind(as_tibble(ol), fc = gr2$signalValue[as.matrix(ol)[,2]])
    FC <- aggregate(fc ~ queryHits, data = FC, mean)
    FC <- left_join(tibble(queryHits = seq(nrow(values(gr1)))), FC, by = "queryHits")
    
    meta_dat <- tibble(peaks = peaks$peaks, FC = FC$fc) 
    return(meta_dat)
}

combine_epic <- function(bed_lf, bed_fl, manorm){
    manorm <- read_tsv(manorm, col_types = cols())
    grMN <- makeGRangesFromDataFrame(manorm, keep.extra.columns = TRUE)
    
    meta_dat_lf <- get_metadat(bed_lf, grMN)
    meta_dat_fl <- get_metadat(bed_fl, grMN)

    values(grMN) <- values(grMN) %>% add_column(peaks_leaf = meta_dat_lf$peaks, 
                          FC_leaf = meta_dat_lf$FC, peaks_infl = meta_dat_fl$peaks, 
                          FC_infl = meta_dat_fl$FC , .before=1) 

    return(grMN)
}

