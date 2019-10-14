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

## scatterplot
GGscatterPlot <- function(data, mapping, ..., 
                        method = "spearman") {

#Get correlation coefficient
    x <- GGally::eval_data_col(data, mapping$x)
    y <- GGally::eval_data_col(data, mapping$y)

    cor <- cor(x, y, method = method)
#Assemble data frame
    df <- data.frame(x = x, y = y)
# PCA
    nonNull <- x!=0 & y!=0
    dfpc <- prcomp(~x+y, df[nonNull,])
    df$cols <- predict(dfpc, df)[,1]
# Define the direction of color range based on PC1 orientation:
    dfsum <- x+y
    colDirection <- ifelse(dfsum[which.max(df$cols)] < 
                               dfsum[which.min(df$cols)],
                           1,
                           -1)
#Get 2D density for alpha
    dens2D <- MASS::kde2d(df$x, df$y)
    df$density <- fields::interp.surface(dens2D , 
                                         df[,c("x", "y")])

if (any(df$density==0)) {
    mini2D = min(df$density[df$density!=0]) #smallest non zero value
    df$density[df$density==0] <- mini2D
}
#Prepare plot
    pp <- ggplot(df, aes(x=x, y=y, color = cols, alpha = 1/density)) +
                ggplot2::geom_point(shape=16, show.legend = FALSE) +
                ggplot2::scale_color_viridis_c(direction = colDirection) +
#                scale_color_gradient(low = "#0091ff", high = "#f0650e") +
                ggplot2::scale_alpha(range = c(.05, .6)) +
                ggplot2::geom_abline(intercept = 0, slope = 1, col="darkred") +
                ggplot2::geom_label(
                        data = data.frame(
                                        xlabel = min(x, na.rm = TRUE),
                                        ylabel = max(y, na.rm = TRUE),
                                        lab = round(cor, digits = 3)),
                        mapping = ggplot2::aes(x = xlabel, 
                                               y = ylabel, 
                                               label = lab),
                        hjust = 0, vjust = 1,
                        size = 3, fontface = "bold",
                        inherit.aes = FALSE # do not inherit anything from the ...
                        ) +
                theme_minimal()

return(pp)
}

